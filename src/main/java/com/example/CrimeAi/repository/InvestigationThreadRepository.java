package com.example.CrimeAi.repository;

import com.example.CrimeAi.entity.InvestigationThread;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface InvestigationThreadRepository extends JpaRepository<InvestigationThread, UUID> {
    List<InvestigationThread> findByCrimeCase_CaseIdAndInvestigatorIdOrderByCreatedAtDesc(String caseId, String investigatorId);
}
