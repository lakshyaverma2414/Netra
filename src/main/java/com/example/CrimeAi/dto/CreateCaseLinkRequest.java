package com.example.CrimeAi.dto;

import jakarta.validation.constraints.NotBlank;

public class CreateCaseLinkRequest {

    @NotBlank(message = "Target case ID is required")
    private String targetCaseId;

    @NotBlank(message = "Link type is required")
    private String linkType;

    public CreateCaseLinkRequest() {
    }

    public String getTargetCaseId() {
        return targetCaseId;
    }

    public void setTargetCaseId(String targetCaseId) {
        this.targetCaseId = targetCaseId;
    }

    public String getLinkType() {
        return linkType;
    }

    public void setLinkType(String linkType) {
        this.linkType = linkType;
    }
}