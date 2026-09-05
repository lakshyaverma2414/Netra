package com.example.CrimeAi.dto;

import java.time.LocalDateTime;

public class CaseLinkResponse {

    private String sourceCaseId;
    private String targetCaseId;
    private String linkType;
    public CaseLinkResponse() {
    }

    public CaseLinkResponse(
            String sourceCaseId,
            String targetCaseId,
            String linkType) {
        this.sourceCaseId = sourceCaseId;
        this.targetCaseId = targetCaseId;
        this.linkType = linkType;
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

    }