package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.AiInvestigationRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class AiServiceClient {

    private final RestTemplate restTemplate;
    
    // Hardcoded for now, could be in application.properties
    private final String aiServiceUrl = "http://127.0.0.1:8000/api/v1/investigations/query";

    public AiServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Object investigate(AiInvestigationRequest request) {
        // Map to expected Python API format: {"case_id": "...", "question": "..."}
        Map<String, String> payload = new HashMap<>();
        payload.put("case_id", request.getCaseId());
        payload.put("question", request.getQuestion());

        ResponseEntity<Object> response = restTemplate.postForEntity(
                aiServiceUrl,
                payload,
                Object.class
        );

        return response.getBody();
    }
}
