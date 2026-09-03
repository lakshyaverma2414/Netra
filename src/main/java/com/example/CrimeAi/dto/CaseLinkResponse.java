package com.example.CrimeAi.dto;

import java.time.LocalDateTime;

public class CaseLinkResponse {

    private String sourceCaseId;
    private String targetCaseId;
    private String linkType;
    private LocalDateTime createdAt;

    public CaseLinkResponse() {
    }

    public CaseLinkResponse(
            String sourceCaseId,
            String targetCaseId,
            String linkType,
            LocalDateTime createdAt
    ) {
        this.sourceCaseId = sourceCaseId;
        this.targetCaseId = targetCaseId;
        this.linkType = linkType;
        this.createdAt = createdAt;
    }

    public String getSourceCaseId() {
        return sourceCaseId;
    }

    public String getTargetCaseId() {
        return targetCaseId;
    }

    public String getLinkType() {
        return linkType;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}