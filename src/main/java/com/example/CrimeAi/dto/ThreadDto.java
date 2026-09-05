package com.example.CrimeAi.dto;

import java.time.LocalDateTime;

public class ThreadDto {
    private String threadId;
    private String caseId;
    private String title;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public ThreadDto(String threadId, String caseId, String title, String status, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.threadId = threadId;
        this.caseId = caseId;
        this.title = title;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public String getThreadId() { return threadId; }
    public String getCaseId() { return caseId; }
    public String getTitle() { return title; }
    public String getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
