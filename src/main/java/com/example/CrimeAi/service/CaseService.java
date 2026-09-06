package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.CaseResponse;
import com.example.CrimeAi.dto.CreateCaseRequest;
import com.example.CrimeAi.entity.Case;
import com.example.CrimeAi.entity.User;
import com.example.CrimeAi.fabric.FabricGatewayService;
import com.example.CrimeAi.repository.CaseRepository;
import com.example.CrimeAi.repository.UserRepository;

import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

@Service
public class CaseService {

    private final CaseRepository caseRepository;
    private final UserRepository userRepository;
    private final FabricGatewayService fabricGatewayService;

    public CaseService(
            CaseRepository caseRepository,
            UserRepository userRepository,
            FabricGatewayService fabricGatewayService) {

        this.caseRepository = caseRepository;
        this.userRepository = userRepository;
        this.fabricGatewayService = fabricGatewayService;
    }

    // =========================================================
    // CREATE CASE
    // =========================================================

    public CaseResponse createCase(CreateCaseRequest request) {

        if (caseRepository.existsById(request.getCaseId())) {
            throw new RuntimeException(
                    "Case already exists: " + request.getCaseId()
            );
        }

        Case crimeCase = new Case();

        crimeCase.setCaseId(request.getCaseId());
        crimeCase.setTitle(request.getTitle());
        crimeCase.setDescription(request.getDescription());

        if (request.getStatus() == null ||
                request.getStatus().isBlank()) {

            crimeCase.setStatus("OPEN");

        } else {
            crimeCase.setStatus(request.getStatus());
        }

        // Find assigned user
        if (request.getAssignedTo() != null &&
                !request.getAssignedTo().isBlank()) {

            User user = userRepository
                    .findByUsername(request.getAssignedTo())
                    .orElseThrow(() ->
                            new RuntimeException(
                                    "User not found: "
                                            + request.getAssignedTo()
                            ));

            crimeCase.setAssignedTo(user);
        }

        // Save in PostgreSQL
        Case savedCase = caseRepository.save(crimeCase);

        // Generate SHA-256 hash
        String dataHash = generateCaseHash(savedCase);

        // Determine actor
        String performedBy = request.getAssignedTo();

        if (performedBy == null || performedBy.isBlank()) {
            performedBy = "SYSTEM";
        }

        // Fabric audit
        createFabricAudit(
                savedCase.getCaseId(),
                "CASE_CREATED",
                performedBy,
                savedCase.getCreatedAt().toString(),
                dataHash
        );

        return convertToResponse(savedCase);
    }

    // =========================================================
    // GET ALL CASES
    // =========================================================

    public List<CaseResponse> getAllCases() {

        return caseRepository.findAll()
                .stream()
                .map(this::convertToResponse)
                .toList();
    }

    // =========================================================
    // GET CASE BY ID
    // =========================================================

    public CaseResponse getCaseById(String caseId) {

        Case crimeCase = caseRepository.findById(caseId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Case not found: " + caseId
                        ));

        return convertToResponse(crimeCase);
    }

    // =========================================================
    // UPDATE CASE
    // =========================================================

    public CaseResponse updateCase(
            String caseId,
            CreateCaseRequest request) {

        Case crimeCase = caseRepository.findById(caseId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Case not found: " + caseId
                        ));

        crimeCase.setTitle(request.getTitle());
        crimeCase.setDescription(request.getDescription());

        if (request.getStatus() != null &&
                !request.getStatus().isBlank()) {

            crimeCase.setStatus(request.getStatus());
        }

        if (request.getAssignedTo() != null &&
                !request.getAssignedTo().isBlank()) {

            User user = userRepository
                    .findByUsername(request.getAssignedTo())
                    .orElseThrow(() ->
                            new RuntimeException(
                                    "User not found: "
                                            + request.getAssignedTo()
                            ));

            crimeCase.setAssignedTo(user);
        }

        // Save updated case in PostgreSQL
        Case updatedCase = caseRepository.save(crimeCase);

        String dataHash = generateCaseHash(updatedCase);

        String performedBy = request.getAssignedTo();

        if (performedBy == null || performedBy.isBlank()) {
            performedBy = "SYSTEM";
        }

        createFabricAudit(
                updatedCase.getCaseId(),
                "CASE_UPDATED",
                performedBy,
                updatedCase.getUpdatedAt().toString(),
                dataHash
        );

        return convertToResponse(updatedCase);
    }

    // =========================================================
    // DELETE CASE
    // =========================================================

    public void deleteCase(String caseId) {

        Case crimeCase = caseRepository.findById(caseId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Case not found: " + caseId
                        ));

        /*
         * Generate hash BEFORE deleting the PostgreSQL record.
         * This allows the deleted case state to be recorded
         * permanently on Fabric.
         */
        String dataHash = generateCaseHash(crimeCase);

        /*
         * Currently we don't have the authenticated user
         * directly inside this service.
         *
         * Therefore SYSTEM is used as fallback.
         */
        String performedBy = "SYSTEM";

        // Delete from PostgreSQL
        caseRepository.delete(crimeCase);

        // Fabric CASE_DELETED audit
        createFabricAudit(
                crimeCase.getCaseId(),
                "CASE_DELETED",
                performedBy,
                java.time.LocalDateTime.now().toString(),
                dataHash
        );
    }

    // =========================================================
    // FABRIC AUDIT HELPER
    // =========================================================

    private void createFabricAudit(
            String caseId,
            String action,
            String performedBy,
            String timestamp,
            String dataHash) {

        try {

            fabricGatewayService.createAudit(
                    caseId,
                    action,
                    performedBy,
                    timestamp,
                    dataHash
            );

            System.out.println(
                    "Fabric audit created successfully"
                            + " | caseId=" + caseId
                            + " | action=" + action
                            + " | performedBy=" + performedBy
            );

        } catch (Exception e) {

            /*
             * PostgreSQL operation has already completed.
             * Fabric failure is logged but does not undo
             * the PostgreSQL operation.
             */
            System.err.println(
                    "WARNING: PostgreSQL operation completed "
                            + "but Fabric audit failed."
            );

            System.err.println(
                    "Fabric error: " + e.getMessage()
            );
        }
    }

    // =========================================================
    // SHA-256 HASH
    // =========================================================

    private String generateCaseHash(Case crimeCase) {

        try {

            String data =
                    crimeCase.getCaseId()
                            + "|"
                            + crimeCase.getTitle()
                            + "|"
                            + crimeCase.getDescription()
                            + "|"
                            + crimeCase.getStatus()
                            + "|"
                            + crimeCase.getCreatedAt();

            MessageDigest digest =
                    MessageDigest.getInstance("SHA-256");

            byte[] hash =
                    digest.digest(
                            data.getBytes(StandardCharsets.UTF_8)
                    );

            StringBuilder hexString =
                    new StringBuilder();

            for (byte b : hash) {

                String hex =
                        Integer.toHexString(0xff & b);

                if (hex.length() == 1) {
                    hexString.append('0');
                }

                hexString.append(hex);
            }

            return "sha256:" + hexString;

        } catch (Exception e) {

            throw new RuntimeException(
                    "Failed to generate case hash",
                    e
            );
        }
    }

    // =========================================================
    // ENTITY → RESPONSE
    // =========================================================

    private CaseResponse convertToResponse(Case crimeCase) {

        String assignedUsername = null;

        if (crimeCase.getAssignedTo() != null) {

            assignedUsername =
                    crimeCase.getAssignedTo().getUsername();
        }

        return new CaseResponse(
                crimeCase.getCaseId(),
                crimeCase.getTitle(),
                crimeCase.getDescription(),
                crimeCase.getStatus(),
                assignedUsername,
                crimeCase.getCreatedAt(),
                crimeCase.getUpdatedAt()
        );
    }
}