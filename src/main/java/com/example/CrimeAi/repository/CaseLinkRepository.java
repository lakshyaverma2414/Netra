package com.example.CrimeAi.repository;

import com.example.CrimeAi.entity.CaseLink;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CaseLinkRepository
        extends JpaRepository<CaseLink, CaseLink.CaseLinkId> {

    List<CaseLink> findBySourceCaseId(String sourceCaseId);

    List<CaseLink> findByTargetCaseId(String targetCaseId);
}