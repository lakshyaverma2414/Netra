package com.example.CrimeAi.dto;

import jakarta.validation.constraints.NotBlank;

public class CreateCaseRequest {

    @NotBlank(message = "Case ID is required")
    private String caseId;

    @NotBlank(message = "Case title is required")
    private String title;

    private String description;

    private String status;

    private String assignedTo;

    public CreateCaseRequest() {
    }

    public String getCaseId() {
        return caseId;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getAssignedTo() {
        return assignedTo;
    }

    public void setAssignedTo(String assignedTo) {
        this.assignedTo = assignedTo;
    }
}