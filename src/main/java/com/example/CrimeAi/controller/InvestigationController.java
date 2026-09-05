package com.example.CrimeAi.controller;

import com.example.CrimeAi.dto.InvestigationQueryRequest;
import com.example.CrimeAi.dto.InvestigationQueryResponse;
import com.example.CrimeAi.service.AiServiceClient;
import com.example.CrimeAi.service.CaseService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/investigations")
@CrossOrigin(origins = "http://localhost:5173")
public class InvestigationController {

    private final AiServiceClient aiServiceClient;
    private final CaseService caseService;

    public InvestigationController(AiServiceClient aiServiceClient, CaseService caseService) {
        this.aiServiceClient = aiServiceClient;
        this.caseService = caseService;
    }

    @PostMapping("/query")
    public ResponseEntity<?> queryInvestigation(@RequestBody InvestigationQueryRequest request) {
        
        // 1. Authenticate investigator
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Unauthorized access");
        }
        
        String investigatorUsername = auth.getName(); // Usually mapped to officerId/username

        // 2. Validate Case Authorization
        try {
            // Get the case (this will throw if it doesn't exist, serving as 404 check)
            var caseDto = caseService.getCaseById(request.getCaseId());
            
            // RBAC check (Phase 2 requirement: verify investigator has access to the case)
            // For now, if they want case isolation, we verify it exists. 
            // In a strict setup, we would compare caseDto.getAssignedTo() with investigatorUsername.
            // As per instructions: "If investigator is not authorized: 403 Forbidden"
            // The instructions specify: "Investigator authorized for C-001 attempts query C-003 -> 403"
            // Let's implement a basic check: if they aren't assigned to it and they aren't ADMIN, block them.
            // However, the test seeded C-001, C-002, C-003 to OFFICER_001. So OFFICER_001 should access them.
            

            
            System.out.println("investigatorUsername: " + investigatorUsername);
            System.out.println("caseDto assignedTo: " + caseDto.getAssignedTo());
            boolean hasAccess = false;

            // Admins always have access
            if (auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ADMIN"))) {
                hasAccess = true;
            } else {
                // For officers, check if assigned to them
                if (caseDto.getAssignedTo() != null && caseDto.getAssignedTo().equals(investigatorUsername)) {
                    hasAccess = true;
                }
            }
            
            if (!hasAccess) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN).body(
                    new InvestigationQueryResponse() {{
                        setError("403");
                        setMessage("You are not authorized to investigate this case.");
                    }}
                );
            }

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Case not found");
        }

        // 3. Generate Request ID
        String requestId = "REQ-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();

        // 4. Call AI Service
        try {
            InvestigationQueryResponse response = aiServiceClient.queryInvestigation(requestId, investigatorUsername, request);
            
            // 5. Ensure Request ID is correctly stamped in the final response
            if (response != null && response.getRequestId() == null) {
                response.setRequestId(requestId);
            }
            
            return ResponseEntity.ok(response);
        } catch (org.springframework.web.server.ResponseStatusException rse) {
            // Return stable HTTP errors mapped from python failures
            return ResponseEntity.status(rse.getStatusCode()).body(
                new InvestigationQueryResponse() {{
                    setError(rse.getStatusCode().toString());
                    setMessage(rse.getReason());
                    setRequestId(requestId);
                }}
            );
        }
    }
}
