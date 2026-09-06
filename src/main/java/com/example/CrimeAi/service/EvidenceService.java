package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.EvidenceResponse;
import com.example.CrimeAi.entity.Evidence;
import com.example.CrimeAi.fabric.FabricGatewayService;
import com.example.CrimeAi.repository.EvidenceRepository;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.time.LocalDateTime;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;

@Service
public class EvidenceService {

    private final EvidenceRepository evidenceRepository;
    private final FabricGatewayService fabricGatewayService;

    @Value("${file.upload-dir}")
    private String uploadDir;


    // =========================
    // Constructor
    // =========================

    public EvidenceService(
            EvidenceRepository evidenceRepository,
            FabricGatewayService fabricGatewayService) {

        this.evidenceRepository = evidenceRepository;
        this.fabricGatewayService = fabricGatewayService;
    }


    // =========================================================
    // UPLOAD EVIDENCE
    // =========================================================

    public EvidenceResponse uploadEvidence(
            String caseId,
            MultipartFile file,
            String uploadedBy) {

        try {

            // -------------------------
            // Validate file
            // -------------------------

            if (file == null || file.isEmpty()) {
                throw new IllegalArgumentException(
                        "Evidence file is required"
                );
            }


            // -------------------------
            // Validate case ID
            // -------------------------

            if (caseId == null || caseId.isBlank()) {
                throw new IllegalArgumentException(
                        "Case ID is required"
                );
            }


            // -------------------------
            // Validate uploadedBy
            // -------------------------

            if (uploadedBy == null || uploadedBy.isBlank()) {
                throw new IllegalArgumentException(
                        "Uploaded by is required"
                );
            }


            // -------------------------
            // Generate Evidence ID
            // -------------------------

            String evidenceId =
                    "EVD-" +
                            UUID.randomUUID()
                                    .toString()
                                    .substring(0, 8)
                                    .toUpperCase();


            // -------------------------
            // Original file name
            // -------------------------

            String originalFileName =
                    file.getOriginalFilename();

            if (originalFileName == null ||
                    originalFileName.isBlank()) {

                throw new IllegalArgumentException(
                        "Invalid file name"
                );
            }


            // -------------------------
            // Calculate SHA-256
            // -------------------------

            byte[] fileBytes = file.getBytes();

            String fileHash =
                    calculateSha256(fileBytes);

            String finalHash =
                    "sha256:" + fileHash;


            // =================================================
            // CREATE UPLOAD DIRECTORY
            // =================================================

            Path uploadPath =
                    Paths.get(uploadDir)
                            .toAbsolutePath()
                            .normalize();

            Files.createDirectories(uploadPath);


            // =================================================
            // CREATE STORED FILE NAME
            // =================================================

            String storedFileName =
                    evidenceId + "_" + originalFileName;


            // =================================================
            // FINAL FILE LOCATION
            // =================================================

            Path destination =
                    uploadPath.resolve(storedFileName)
                            .normalize();


            // =================================================
            // SAVE FILE TO DISK
            // =================================================

            Files.write(destination, fileBytes);


            System.out.println();
            System.out.println("==========================================");
            System.out.println("EVIDENCE FILE SAVED");
            System.out.println("==========================================");
            System.out.println("Evidence ID : " + evidenceId);
            System.out.println("Case ID     : " + caseId);
            System.out.println("File Name   : " + originalFileName);
            System.out.println("File Path   : " + destination);
            System.out.println("File Hash   : " + finalHash);
            System.out.println("==========================================");


            // =================================================
            // CREATE EVIDENCE ENTITY
            // =================================================

            Evidence evidence = new Evidence();

            evidence.setEvidenceId(evidenceId);
            evidence.setCaseId(caseId);
            evidence.setFileName(originalFileName);
            evidence.setFileType(file.getContentType());

            // IMPORTANT
            // Actual physical file path is stored in DB
            evidence.setFilePath(destination.toString());

            evidence.setFileHash(finalHash);
            evidence.setUploadedBy(uploadedBy);


            // =================================================
            // SAVE EVIDENCE TO POSTGRESQL
            // =================================================

            Evidence savedEvidence =
                    evidenceRepository.save(evidence);


            System.out.println();
            System.out.println("==========================================");
            System.out.println("EVIDENCE SAVED TO POSTGRESQL");
            System.out.println("==========================================");
            System.out.println("Evidence ID : "
                    + savedEvidence.getEvidenceId());

            System.out.println("File Path   : "
                    + savedEvidence.getFilePath());

            System.out.println("File Hash   : "
                    + savedEvidence.getFileHash());

            System.out.println("Uploaded By : "
                    + savedEvidence.getUploadedBy());

            System.out.println("Uploaded At : "
                    + savedEvidence.getUploadedAt());

            System.out.println("==========================================");


            // =================================================
            // FABRIC AUDIT
            // =================================================

            try {

                String fabricResult =
                        fabricGatewayService.createAudit(
                                caseId,
                                "EVIDENCE_ADDED",
                                uploadedBy,
                                savedEvidence
                                        .getUploadedAt()
                                        .toString(),
                                savedEvidence.getFileHash()
                        );


                System.out.println();
                System.out.println(
                        "=========================================="
                );
                System.out.println(
                        "FABRIC EVIDENCE AUDIT CREATED"
                );
                System.out.println(
                        "=========================================="
                );

                System.out.println("Case ID     : "
                        + caseId);

                System.out.println("Evidence ID : "
                        + evidenceId);

                System.out.println("Hash        : "
                        + savedEvidence.getFileHash());

                System.out.println("Fabric      : "
                        + fabricResult);

                System.out.println(
                        "=========================================="
                );

            } catch (Exception fabricException) {

                System.err.println();
                System.err.println(
                        "WARNING: Evidence saved in PostgreSQL"
                );

                System.err.println(
                        "but Fabric audit failed."
                );

                System.err.println(
                        "Fabric error: "
                                + fabricException.getMessage()
                );
            }


            // =================================================
            // RETURN RESPONSE
            // =================================================

            return mapToResponse(savedEvidence);


        } catch (Exception e) {

            e.printStackTrace();

            throw new RuntimeException(
                    "Evidence upload failed: "
                            + e.getMessage(),
                    e
            );
        }
    }


    // =========================================================
    // GET EVIDENCE BY CASE ID
    // =========================================================

    public List<EvidenceResponse> getEvidenceByCaseId(
            String caseId) {

        return evidenceRepository
                .findByCaseId(caseId)
                .stream()
                .map(this::mapToResponse)
                .toList();
    }


    // =========================================================
    // VERIFY EVIDENCE INTEGRITY
    // =========================================================

    public boolean verifyEvidence(
            String evidenceId) {

        try {

            System.out.println();
            System.out.println(
                    "=========================================="
            );
            System.out.println(
                    "EVIDENCE INTEGRITY VERIFICATION"
            );
            System.out.println(
                    "=========================================="
            );

            System.out.println(
                    "Evidence ID : " + evidenceId
            );


            // =================================================
            // FIND EVIDENCE FROM DATABASE
            // =================================================

            Evidence evidence =
                    evidenceRepository
                            .findByEvidenceId(evidenceId)
                            .orElseThrow(() ->
                                    new RuntimeException(
                                            "Evidence not found: "
                                                    + evidenceId
                                    )
                            );


            // =================================================
            // GET STORED FILE PATH
            // =================================================

            String storedFilePath =
                    evidence.getFilePath();


            System.out.println(
                    "Stored File Path : "
                            + storedFilePath
            );


            // =================================================
            // CHECK FILE PATH
            // =================================================

            if (storedFilePath == null ||
                    storedFilePath.isBlank()) {

                throw new RuntimeException(
                        "File path is missing in database for evidence: "
                                + evidenceId
                );
            }


            // =================================================
            // CREATE PATH
            // =================================================

            Path filePath =
                    Paths.get(storedFilePath);


            // =================================================
            // CHECK FILE EXISTS
            // =================================================

            if (!Files.exists(filePath)) {

                throw new RuntimeException(
                        "Evidence file not found: "
                                + filePath
                );
            }


            // =================================================
            // READ CURRENT FILE
            // =================================================

            byte[] fileData =
                    Files.readAllBytes(filePath);


            // =================================================
            // CALCULATE CURRENT HASH
            // =================================================

            String currentHash =
                    calculateSha256(fileData);


            String currentHashWithPrefix =
                    "sha256:" + currentHash;


            // =================================================
            // GET STORED HASH
            // =================================================

            String storedHash =
                    evidence.getFileHash();


            // =================================================
            // COMPARE HASHES
            // =================================================

            boolean verified =
                    storedHash != null &&
                            storedHash.equalsIgnoreCase(
                                    currentHashWithPrefix
                            );


            // =================================================
            // LOG RESULT
            // =================================================

            System.out.println(
                    "Stored Hash  : "
                            + storedHash
            );

            System.out.println(
                    "Current Hash : "
                            + currentHashWithPrefix
            );

            System.out.println(
                    "Verified     : "
                            + verified
            );

            System.out.println(
                    "=========================================="
            );


            return verified;


        } catch (Exception e) {

            e.printStackTrace();

            throw new RuntimeException(
                    "Evidence verification failed: "
                            + e.getMessage(),
                    e
            );
        }
    }


    // =========================================================
    // SHA-256 HASH
    // =========================================================

    private String calculateSha256(
            byte[] data) throws Exception {

        MessageDigest digest =
                MessageDigest.getInstance("SHA-256");

        byte[] hash =
                digest.digest(data);

        return HexFormat
                .of()
                .formatHex(hash);
    }


    // =========================================================
    // ENTITY -> RESPONSE DTO
    // =========================================================

    private EvidenceResponse mapToResponse(
            Evidence evidence) {

        return new EvidenceResponse(

                evidence.getEvidenceId(),

                evidence.getCaseId(),

                evidence.getFileName(),

                evidence.getFileType(),

                evidence.getFileHash(),

                evidence.getUploadedBy(),

                evidence.getUploadedAt()
        );
    }
    public byte[] downloadEvidence(String evidenceId) {

        try {
            Evidence evidence = evidenceRepository
                    .findByEvidenceId(evidenceId)
                    .orElseThrow(() ->
                            new RuntimeException(
                                    "Evidence not found: " + evidenceId
                            )
                    );

            String filePath = evidence.getFilePath();

            if (filePath == null || filePath.isBlank()) {
                throw new RuntimeException(
                        "File path is missing for evidence: " + evidenceId
                );
            }

            Path path = Paths.get(filePath);

            if (!Files.exists(path)) {
                throw new RuntimeException(
                        "Evidence file not found: " + path
                );
            }

            return Files.readAllBytes(path);

        } catch (Exception e) {
            throw new RuntimeException(
                    "Evidence download failed: " + e.getMessage(),
                    e
            );
        }
    }
    public Evidence getEvidenceById(String evidenceId) {

        return evidenceRepository
                .findByEvidenceId(evidenceId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Evidence not found: " + evidenceId
                        )
                );
    }
}