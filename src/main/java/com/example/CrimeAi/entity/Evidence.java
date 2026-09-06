package com.example.CrimeAi.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "evidence")
public class Evidence {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "evidence_id", nullable = false, unique = true, length = 100)
    private String evidenceId;

    @Column(name = "case_id", nullable = false, length = 50)
    private String caseId;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Column(name = "file_type")
    private String fileType;

    @Column(name = "file_path")
    private String filePath;

    @Column(name = "file_hash", nullable = false, length = 100)
    private String fileHash;

    @Column(name = "uploaded_by")
    private String uploadedBy;

    @Column(name = "uploaded_at")
    private LocalDateTime uploadedAt;


    // =========================
    // Default Constructor
    // =========================

    public Evidence() {
    }


    // =========================
    // Auto Set Upload Time
    // =========================

    @PrePersist
    protected void onCreate() {
        uploadedAt = LocalDateTime.now();
    }


    // =========================
    // Getters
    // =========================

    public Long getId() {
        return id;
    }

    public String getEvidenceId() {
        return evidenceId;
    }

    public String getCaseId() {
        return caseId;
    }

    public String getFileName() {
        return fileName;
    }

    public String getFileType() {
        return fileType;
    }

    public String getFilePath() {
        return filePath;
    }

    public String getFileHash() {
        return fileHash;
    }

    public String getUploadedBy() {
        return uploadedBy;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }


    // =========================
    // Setters
    // =========================

    public void setEvidenceId(String evidenceId) {
        this.evidenceId = evidenceId;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public void setFileType(String fileType) {
        this.fileType = fileType;
    }

    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    public void setFileHash(String fileHash) {
        this.fileHash = fileHash;
    }

    public void setUploadedBy(String uploadedBy) {
        this.uploadedBy = uploadedBy;
    }

    public void setUploadedAt(LocalDateTime uploadedAt) {
        this.uploadedAt = uploadedAt;
    }
}