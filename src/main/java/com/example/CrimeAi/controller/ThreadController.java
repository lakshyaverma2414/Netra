package com.example.CrimeAi.controller;

import com.example.CrimeAi.dto.CreateThreadRequest;
import com.example.CrimeAi.dto.ThreadDto;
import com.example.CrimeAi.entity.Case;
import com.example.CrimeAi.entity.InvestigationThread;
import com.example.CrimeAi.repository.CaseRepository;
import com.example.CrimeAi.repository.InvestigationThreadRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/investigations/threads")
@CrossOrigin(origins = "http://localhost:5173")
public class ThreadController {

    private final InvestigationThreadRepository threadRepository;
    private final CaseRepository caseRepository;

    public ThreadController(InvestigationThreadRepository threadRepository, CaseRepository caseRepository) {
        this.threadRepository = threadRepository;
        this.caseRepository = caseRepository;
    }

    @PostMapping
    public ResponseEntity<?> createThread(@RequestBody CreateThreadRequest request) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        
        String username = auth.getName();
        
        Case crimeCase = caseRepository.findById(request.getCaseId()).orElse(null);
        if (crimeCase == null) return ResponseEntity.notFound().build();
        
        // Basic Authorization check
        boolean hasAccess = auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ADMIN")) ||
                           (crimeCase.getAssignedTo() != null && crimeCase.getAssignedTo().getUsername().equals(username));
                           
        if (!hasAccess) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        
        InvestigationThread thread = new InvestigationThread();
        thread.setCrimeCase(crimeCase);
        thread.setInvestigatorId(username);
        thread.setTitle(request.getTitle() != null ? request.getTitle() : "New Investigation");
        
        InvestigationThread saved = threadRepository.save(thread);
        return ResponseEntity.ok(convertToDto(saved));
    }

    @GetMapping
    public ResponseEntity<?> listThreads(@RequestParam("caseId") String caseId) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String username = auth.getName();
        
        List<InvestigationThread> threads = threadRepository.findByCrimeCase_CaseIdAndInvestigatorIdOrderByCreatedAtDesc(caseId, username);
        List<ThreadDto> dtos = threads.stream().map(this::convertToDto).collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }
    
    private ThreadDto convertToDto(InvestigationThread t) {
        return new ThreadDto(
            t.getThreadId().toString(),
            t.getCrimeCase().getCaseId(),
            t.getTitle(),
            t.getStatus(),
            t.getCreatedAt(),
            t.getUpdatedAt()
        );
    }
}
