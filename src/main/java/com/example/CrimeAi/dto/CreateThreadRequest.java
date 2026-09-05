package com.example.CrimeAi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class CreateThreadRequest {
    @JsonProperty("case_id")
    private String caseId;
    
    private String title;

    public String getCaseId() { return caseId; }
    public void setCaseId(String caseId) { this.caseId = caseId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
}
