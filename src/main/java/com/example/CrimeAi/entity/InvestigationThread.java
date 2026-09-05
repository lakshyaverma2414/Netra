package com.example.CrimeAi.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "investigation_threads")
public class InvestigationThread {

    @Id
    @Column(name = "thread_id")
    private UUID threadId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "case_id", nullable = false)
    private Case crimeCase;

    @Column(name = "investigator_id", nullable = false)
    private String investigatorId;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String status; // ACTIVE, ARCHIVED

    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", insertable = false, updatable = false)
    private LocalDateTime updatedAt;

    public InvestigationThread() {
        this.threadId = UUID.randomUUID();
        this.status = "ACTIVE";
    }

    public UUID getThreadId() { return threadId; }
    public void setThreadId(UUID threadId) { this.threadId = threadId; }

    public Case getCrimeCase() { return crimeCase; }
    public void setCrimeCase(Case crimeCase) { this.crimeCase = crimeCase; }

    public String getInvestigatorId() { return investigatorId; }
    public void setInvestigatorId(String investigatorId) { this.investigatorId = investigatorId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
