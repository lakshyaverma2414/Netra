package com.example.CrimeAi.repository;

import com.example.CrimeAi.entity.Evidence;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface EvidenceRepository extends JpaRepository<Evidence, Long> {

    Optional<Evidence> findByEvidenceId(String evidenceId);

    List<Evidence> findByCaseId(String caseId);
}