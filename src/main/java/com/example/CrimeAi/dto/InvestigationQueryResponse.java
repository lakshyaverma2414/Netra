package com.example.CrimeAi.dto;

import java.util.List;
import java.util.Map;

public class InvestigationQueryResponse {
    private String requestId;

    @com.fasterxml.jackson.annotation.JsonProperty("thread_id")
    private String threadId;
    private String answer;
    private List<Map<String, Object>> entities;
    private List<Map<String, Object>> relationships;
    private List<Map<String, Object>> findings;
    private List<Map<String, Object>> evidence;
    private List<Map<String, Object>> trace;
    private String error;
    private String message;

    public InvestigationQueryResponse() {}

    public String getThreadId() { return threadId; }
    public void setThreadId(String threadId) { this.threadId = threadId; }

    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }

    public String getAnswer() { return answer; }
    public void setAnswer(String answer) { this.answer = answer; }

    public List<Map<String, Object>> getEntities() { return entities; }
    public void setEntities(List<Map<String, Object>> entities) { this.entities = entities; }

    public List<Map<String, Object>> getRelationships() { return relationships; }
    public void setRelationships(List<Map<String, Object>> relationships) { this.relationships = relationships; }

    public List<Map<String, Object>> getFindings() { return findings; }
    public void setFindings(List<Map<String, Object>> findings) { this.findings = findings; }

    public List<Map<String, Object>> getEvidence() { return evidence; }
    public void setEvidence(List<Map<String, Object>> evidence) { this.evidence = evidence; }

    public List<Map<String, Object>> getTrace() { return trace; }
    public void setTrace(List<Map<String, Object>> trace) { this.trace = trace; }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
