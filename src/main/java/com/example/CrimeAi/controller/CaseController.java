package com.example.CrimeAi.controller;

import com.example.CrimeAi.dto.CaseResponse;
import com.example.CrimeAi.dto.CreateCaseRequest;
import com.example.CrimeAi.service.CaseService;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cases")
@CrossOrigin(origins = "http://localhost:5173")
public class CaseController {

    private final CaseService caseService;

    public CaseController(CaseService caseService) {
        this.caseService = caseService;
    }

    @PostMapping
    public ResponseEntity<CaseResponse> createCase(
            @Valid @RequestBody CreateCaseRequest request) {

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(caseService.createCase(request));
    }

    @GetMapping
    public ResponseEntity<List<CaseResponse>> getAllCases() {

        return ResponseEntity.ok(
                caseService.getAllCases()
        );
    }

    @GetMapping("/{caseId}")
    public ResponseEntity<CaseResponse> getCase(
            @PathVariable String caseId) {

        return ResponseEntity.ok(
                caseService.getCaseById(caseId)
        );
    }

    @PutMapping("/{caseId}")
    public ResponseEntity<CaseResponse> updateCase(
            @PathVariable String caseId,
            @Valid @RequestBody CreateCaseRequest request) {

        return ResponseEntity.ok(
                caseService.updateCase(caseId, request)
        );
    }

    @DeleteMapping("/{caseId}")
    public ResponseEntity<String> deleteCase(
            @PathVariable String caseId) {

        caseService.deleteCase(caseId);

        return ResponseEntity.ok(
                "Case deleted successfully: " + caseId
        );
    }
}