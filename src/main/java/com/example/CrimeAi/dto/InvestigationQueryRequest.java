package com.example.CrimeAi.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class InvestigationQueryRequest {
    @JsonProperty("case_id")
    private String caseId;
    
    @JsonProperty("thread_id")
    private String threadId;

    private String question;

    public InvestigationQueryRequest() {}

    public String getCaseId() { return caseId; }
    public void setCaseId(String caseId) { this.caseId = caseId; }

    public String getThreadId() { return threadId; }
    public void setThreadId(String threadId) { this.threadId = threadId; }

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
}
