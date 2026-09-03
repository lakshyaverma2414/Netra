package com.example.CrimeAi.dto;

import java.time.LocalDateTime;

public class CaseResponse {

    private String caseId;
    private String title;
    private String description;
    private String status;
    private String assignedTo;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public CaseResponse() {
    }

    public CaseResponse(
            String caseId,
            String title,
            String description,
            String status,
            String assignedTo,
            LocalDateTime createdAt,
            LocalDateTime updatedAt) {

        this.caseId = caseId;
        this.title = title;
        this.description = description;
        this.status = status;
        this.assignedTo = assignedTo;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public String getCaseId() {
        return caseId;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public String getStatus() {
        return status;
    }

    public String getAssignedTo() {
        return assignedTo;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
}