package com.example.CrimeAi.dto;

import jakarta.validation.constraints.NotBlank;

public class AiInvestigationRequest {

    @NotBlank(message = "Case ID is required")
    private String caseId;

    @NotBlank(message = "Question is required")
    private String question;

    public AiInvestigationRequest() {}

    public AiInvestigationRequest(String caseId, String question) {
        this.caseId = caseId;
        this.question = question;
    }

    public String getCaseId() {
        return caseId;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }
}
