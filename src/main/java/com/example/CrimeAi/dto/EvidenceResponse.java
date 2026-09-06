package com.example.CrimeAi.dto;

import java.time.LocalDateTime;

public class EvidenceResponse {

    private String evidenceId;
    private String caseId;
    private String fileName;
    private String fileType;
    private String fileHash;
    private String uploadedBy;
    private LocalDateTime uploadedAt;

    public EvidenceResponse() {
    }

    public EvidenceResponse(
            String evidenceId,
            String caseId,
            String fileName,
            String fileType,
            String fileHash,
            String uploadedBy,
            LocalDateTime uploadedAt) {

        this.evidenceId = evidenceId;
        this.caseId = caseId;
        this.fileName = fileName;
        this.fileType = fileType;
        this.fileHash = fileHash;
        this.uploadedBy = uploadedBy;
        this.uploadedAt = uploadedAt;
    }

    public String getEvidenceId() {
        return evidenceId;
    }

    public void setEvidenceId(String evidenceId) {
        this.evidenceId = evidenceId;
    }

    public String getCaseId() {
        return caseId;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getFileType() {
        return fileType;
    }

    public void setFileType(String fileType) {
        this.fileType = fileType;
    }

    public String getFileHash() {
        return fileHash;
    }

    public void setFileHash(String fileHash) {
        this.fileHash = fileHash;
    }

    public String getUploadedBy() {
        return uploadedBy;
    }

    public void setUploadedBy(String uploadedBy) {
        this.uploadedBy = uploadedBy;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }

    public void setUploadedAt(LocalDateTime uploadedAt) {
        this.uploadedAt = uploadedAt;
    }
}