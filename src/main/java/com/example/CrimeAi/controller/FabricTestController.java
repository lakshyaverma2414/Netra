package com.example.CrimeAi.controller;

import com.example.CrimeAi.fabric.FabricGatewayService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/fabric")
public class FabricTestController {

    private final FabricGatewayService fabricGatewayService;

    public FabricTestController(
            FabricGatewayService fabricGatewayService
    ) {
        this.fabricGatewayService = fabricGatewayService;
    }

    /**
     * Create an audit record on Hyperledger Fabric
     *
     * POST /api/fabric/audit
     */
    @PostMapping("/audit")
    public ResponseEntity<String> createAudit(
            @RequestParam String caseId,
            @RequestParam String action,
            @RequestParam String performedBy,
            @RequestParam String timestamp,
            @RequestParam String dataHash
    ) {

        String result = fabricGatewayService.createAudit(
                caseId,
                action,
                performedBy,
                timestamp,
                dataHash
        );

        return ResponseEntity.ok(result);
    }

    /**
     * Get all audit records for a case
     *
     * GET /api/fabric/audit/{caseId}
     */
    @GetMapping("/audit/{caseId}")
    public ResponseEntity<String> getCaseAudits(
            @PathVariable String caseId
    ) {

        String result =
                fabricGatewayService.getCaseAudits(caseId);

        return ResponseEntity.ok(result);
    }
}