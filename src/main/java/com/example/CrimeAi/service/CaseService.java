package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.CaseResponse;
import com.example.CrimeAi.dto.CreateCaseRequest;
import com.example.CrimeAi.entity.Case;
import com.example.CrimeAi.entity.User;
import com.example.CrimeAi.repository.CaseRepository;
import com.example.CrimeAi.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CaseService {

    private final CaseRepository caseRepository;
    private final UserRepository userRepository;

    public CaseService(
            CaseRepository caseRepository,
            UserRepository userRepository) {

        this.caseRepository = caseRepository;
        this.userRepository = userRepository;
    }

    public CaseResponse createCase(CreateCaseRequest request) {

        if (caseRepository.existsById(request.getCaseId())) {
            throw new RuntimeException("Case already exists: " + request.getCaseId());
        }

        Case crimeCase = new Case();

        crimeCase.setCaseId(request.getCaseId());
        crimeCase.setTitle(request.getTitle());
        crimeCase.setDescription(request.getDescription());

        if (request.getStatus() == null || request.getStatus().isBlank()) {
            crimeCase.setStatus("OPEN");
        } else {
            crimeCase.setStatus(request.getStatus());
        }

        if (request.getAssignedTo() != null &&
                !request.getAssignedTo().isBlank()) {

            User user = userRepository
                    .findByUsername(request.getAssignedTo())
                    .orElseThrow(() ->
                            new RuntimeException(
                                    "User not found: " + request.getAssignedTo()
                            ));

            crimeCase.setAssignedTo(user);
        }

        Case savedCase = caseRepository.save(crimeCase);

        return convertToResponse(savedCase);
    }

    public List<CaseResponse> getAllCases() {

        return caseRepository.findAll()
                .stream()
                .map(this::convertToResponse)
                .toList();
    }

    public CaseResponse getCaseById(String caseId) {

        Case crimeCase = caseRepository.findById(caseId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Case not found: " + caseId
                        ));

        return convertToResponse(crimeCase);
    }

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
                                    "User not found: " + request.getAssignedTo()
                            ));

            crimeCase.setAssignedTo(user);
        }

        Case updatedCase = caseRepository.save(crimeCase);

        return convertToResponse(updatedCase);
    }

    public void deleteCase(String caseId) {

        if (!caseRepository.existsById(caseId)) {
            throw new RuntimeException(
                    "Case not found: " + caseId
            );
        }

        caseRepository.deleteById(caseId);
    }

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