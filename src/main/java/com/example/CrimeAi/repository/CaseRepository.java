package com.example.CrimeAi.repository;

import com.example.CrimeAi.entity.Case;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CaseRepository extends JpaRepository<Case, String> {
}