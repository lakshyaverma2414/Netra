package com.example.CrimeAi.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.time.LocalDateTime;

@Entity
@Table(name = "case_links")
@IdClass(CaseLink.CaseLinkId.class)
public class CaseLink {

    @Id
    @Column(name = "source_case_id", nullable = false)
    private String sourceCaseId;

    @Id
    @Column(name = "target_case_id", nullable = false)
    private String targetCaseId;

    @Column(name = "link_type", nullable = false, length = 100)
    private String linkType;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    public CaseLink() {
    }

    public CaseLink(
            String sourceCaseId,
            String targetCaseId,
            String linkType
    ) {
        this.sourceCaseId = sourceCaseId;
        this.targetCaseId = targetCaseId;
        this.linkType = linkType;
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public String getSourceCaseId() {
        return sourceCaseId;
    }

    public void setSourceCaseId(String sourceCaseId) {
        this.sourceCaseId = sourceCaseId;
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

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public static class CaseLinkId implements Serializable {

        private String sourceCaseId;
        private String targetCaseId;

        public CaseLinkId() {
        }

        public CaseLinkId(
                String sourceCaseId,
                String targetCaseId
        ) {
            this.sourceCaseId = sourceCaseId;
            this.targetCaseId = targetCaseId;
        }

        public String getSourceCaseId() {
            return sourceCaseId;
        }

        public void setSourceCaseId(String sourceCaseId) {
            this.sourceCaseId = sourceCaseId;
        }

        public String getTargetCaseId() {
            return targetCaseId;
        }

        public void setTargetCaseId(String targetCaseId) {
            this.targetCaseId = targetCaseId;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;

            if (!(o instanceof CaseLinkId)) return false;

            CaseLinkId that = (CaseLinkId) o;

            return sourceCaseId.equals(that.sourceCaseId)
                    && targetCaseId.equals(that.targetCaseId);
        }

        @Override
        public int hashCode() {
            return 31 * sourceCaseId.hashCode()
                    + targetCaseId.hashCode();
        }
    }
}