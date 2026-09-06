package com.example.CrimeAi.controller;

import com.example.CrimeAi.dto.EvidenceResponse;
import com.example.CrimeAi.entity.Evidence;
import com.example.CrimeAi.service.EvidenceService;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/evidence")
@CrossOrigin(origins = "http://localhost:5173")
public class EvidenceController {

    private final EvidenceService evidenceService;

    public EvidenceController(EvidenceService evidenceService) {
        this.evidenceService = evidenceService;
    }


    // =========================================================
    // UPLOAD EVIDENCE
    // =========================================================

    @PostMapping(
            value = "/upload",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public ResponseEntity<EvidenceResponse> uploadEvidence(
            @RequestParam String caseId,
            @RequestParam MultipartFile file,
            @RequestParam String uploadedBy) {

        EvidenceResponse response =
                evidenceService.uploadEvidence(
                        caseId,
                        file,
                        uploadedBy
                );

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }


    // =========================================================
    // GET EVIDENCE BY CASE
    // =========================================================

    @GetMapping("/case/{caseId}")
    public ResponseEntity<List<EvidenceResponse>> getEvidence(
            @PathVariable String caseId) {

        return ResponseEntity.ok(
                evidenceService.getEvidenceByCaseId(caseId)
        );
    }


    // =========================================================
    // VERIFY EVIDENCE INTEGRITY
    // =========================================================

    @GetMapping("/{evidenceId}/verify")
    public ResponseEntity<String> verifyEvidence(
            @PathVariable String evidenceId) {

        boolean verified =
                evidenceService.verifyEvidence(evidenceId);

        if (verified) {

            return ResponseEntity.ok(
                    "Evidence integrity verified successfully"
            );
        }

        return ResponseEntity
                .status(HttpStatus.CONFLICT)
                .body(
                        "Evidence integrity verification failed - "
                                + "file may have been modified"
                );
    }


    // =========================================================
    // DOWNLOAD EVIDENCE
    // =========================================================

    @GetMapping("/{evidenceId}/download")
    public ResponseEntity<byte[]> downloadEvidence(
            @PathVariable String evidenceId) {

        Evidence evidence =
                evidenceService.getEvidenceById(evidenceId);

        byte[] fileData =
                evidenceService.downloadEvidence(evidenceId);

        MediaType mediaType =
                MediaType.APPLICATION_OCTET_STREAM;

        if (evidence.getFileType() != null &&
                !evidence.getFileType().isBlank()) {

            try {
                mediaType =
                        MediaType.parseMediaType(
                                evidence.getFileType()
                        );
            } catch (Exception ignored) {
                // Keep default application/octet-stream
            }
        }

        return ResponseEntity.ok()
                .header(
                        HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"" +
                                evidence.getFileName() +
                                "\""
                )
                .contentType(mediaType)
                .body(fileData);
    }
}