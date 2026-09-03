package com.example.CrimeAi.controller;

import com.example.CrimeAi.dto.CaseLinkResponse;
import com.example.CrimeAi.dto.CreateCaseLinkRequest;
import com.example.CrimeAi.service.CaseLinkService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cases")
public class CaseLinkController {

    private final CaseLinkService caseLinkService;

    public CaseLinkController(
            CaseLinkService caseLinkService
    ) {
        this.caseLinkService = caseLinkService;
    }

    // CREATE LINK
    @PostMapping("/{caseId}/links")
    public ResponseEntity<CaseLinkResponse> createLink(
            @PathVariable String caseId,
            @Valid @RequestBody CreateCaseLinkRequest request
    ) {

        CaseLinkResponse response =
                caseLinkService.createLink(
                        caseId,
                        request
                );

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    // GET LINKS
    @GetMapping("/{caseId}/links")
    public ResponseEntity<List<CaseLinkResponse>> getLinks(
            @PathVariable String caseId
    ) {

        return ResponseEntity.ok(
                caseLinkService.getLinks(caseId)
        );
    }

    // DELETE LINK
    @DeleteMapping("/{caseId}/links/{targetCaseId}")
    public ResponseEntity<Void> deleteLink(
            @PathVariable String caseId,
            @PathVariable String targetCaseId
    ) {

        caseLinkService.deleteLink(
                caseId,
                targetCaseId
        );

        return ResponseEntity.noContent().build();
    }
}