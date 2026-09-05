package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.InvestigationQueryRequest;
import com.example.CrimeAi.dto.InvestigationQueryResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
import java.util.Map;
import java.util.HashMap;

@Service
public class AiServiceClient {

    private final RestTemplate restTemplate;
    
    @Value("${ai.service.base-url:http://127.0.0.1:8000}")
    private String aiServiceBaseUrl;

    public AiServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public InvestigationQueryResponse queryInvestigation(String requestId, String investigatorId, InvestigationQueryRequest request) {
        String url = aiServiceBaseUrl + "/api/v1/investigations/query";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        Map<String, Object> body = new HashMap<>();
        body.put("case_id", request.getCaseId());
        body.put("question", request.getQuestion());
        body.put("request_id", requestId);
        body.put("investigator_id", investigatorId);
        
        if (request.getThreadId() != null) {
            body.put("thread_id", request.getThreadId());
        }

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            return restTemplate.postForObject(url, entity, InvestigationQueryResponse.class);
        } catch (ResourceAccessException e) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "Investigation AI service is temporarily unavailable.", e);
        } catch (HttpStatusCodeException e) {
            if (e.getStatusCode() == HttpStatus.GATEWAY_TIMEOUT) {
                throw new ResponseStatusException(HttpStatus.GATEWAY_TIMEOUT, "Investigation AI service timed out.", e);
            }
            throw new ResponseStatusException(e.getStatusCode(), "Error from AI Service: " + e.getResponseBodyAsString(), e);
        }
    }
}
