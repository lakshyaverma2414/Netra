package com.example.CrimeAi.controller;

import com.example.CrimeAi.dto.AiInvestigationRequest;
import com.example.CrimeAi.service.AiServiceClient;

import jakarta.validation.Valid;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/internal/ai")
@CrossOrigin(origins = "http://localhost:5173")
public class AiController {

    private final AiServiceClient aiServiceClient;

    public AiController(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    @PostMapping("/investigate")
    public ResponseEntity<Object> investigate(
            @Valid @RequestBody AiInvestigationRequest request) {

        return ResponseEntity.ok(
                aiServiceClient.investigate(request)
        );
    }
}
