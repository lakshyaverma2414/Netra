package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.CaseLinkResponse;
import com.example.CrimeAi.dto.CreateCaseLinkRequest;
import com.example.CrimeAi.entity.Case;
import com.example.CrimeAi.entity.CaseLink;
import com.example.CrimeAi.repository.CaseLinkRepository;
import com.example.CrimeAi.repository.CaseRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CaseLinkService {

    private final CaseLinkRepository caseLinkRepository;
    private final CaseRepository caseRepository;

    public CaseLinkService(
            CaseLinkRepository caseLinkRepository,
            CaseRepository caseRepository
    ) {
        this.caseLinkRepository = caseLinkRepository;
        this.caseRepository = caseRepository;
    }

    public CaseLinkResponse createLink(
            String sourceCaseId,
            CreateCaseLinkRequest request
    ) {

        Case sourceCase = caseRepository
                .findById(sourceCaseId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Source case not found: " + sourceCaseId
                        )
                );

        Case targetCase = caseRepository
                .findById(request.getTargetCaseId())
                .orElseThrow(() ->
                        new RuntimeException(
                                "Target case not found: "
                                        + request.getTargetCaseId()
                        )
                );

        CaseLink.CaseLinkId id =
                new CaseLink.CaseLinkId(
                        sourceCase.getCaseId(),
                        targetCase.getCaseId()
                );

        if (caseLinkRepository.existsById(id)) {
            throw new RuntimeException(
                    "Case link already exists"
            );
        }

        CaseLink caseLink = new CaseLink(
                sourceCase.getCaseId(),
                targetCase.getCaseId(),
                request.getLinkType()
        );

        CaseLink saved = caseLinkRepository.save(caseLink);

        return convertToResponse(saved);
    }

    public List<CaseLinkResponse> getLinks(
            String caseId
    ) {

        return caseLinkRepository
                .findBySourceCaseId(caseId)
                .stream()
                .map(this::convertToResponse)
                .toList();
    }

    public void deleteLink(
            String sourceCaseId,
            String targetCaseId
    ) {

        CaseLink.CaseLinkId id =
                new CaseLink.CaseLinkId(
                        sourceCaseId,
                        targetCaseId
                );

        if (!caseLinkRepository.existsById(id)) {
            throw new RuntimeException(
                    "Case link not found"
            );
        }

        caseLinkRepository.deleteById(id);
    }

    private CaseLinkResponse convertToResponse(
            CaseLink caseLink
    ) {

        return new CaseLinkResponse(
                caseLink.getSourceCaseId(),
                caseLink.getTargetCaseId(),
                caseLink.getLinkReason()
                
        );
    }
}