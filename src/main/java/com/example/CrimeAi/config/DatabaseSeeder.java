package com.example.CrimeAi.config;

import com.example.CrimeAi.entity.User;
import com.example.CrimeAi.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class DatabaseSeeder implements CommandLineRunner {

    private final UserRepository userRepository;
    private final JdbcTemplate jdbcTemplate;
    private final PasswordEncoder passwordEncoder;

    public DatabaseSeeder(UserRepository userRepository, JdbcTemplate jdbcTemplate, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.jdbcTemplate = jdbcTemplate;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        if (userRepository.findByUsername("OFFICER_001").isEmpty()) {
            System.out.println("Seeding dev officer accounts...");
            String password = passwordEncoder.encode("password123");

            User officer1 = new User("OFFICER_001", "Inspector Vikram", password, "OFFICER");
            User officer2 = new User("OFFICER_002", "Inspector Aisha", password, "OFFICER");
            User supervisor = new User("SUPERVISOR_001", "ACP Sharma", password, "SUPERVISOR");
            User admin = new User("ADMIN_001", "System Admin", password, "ADMIN");

            userRepository.saveAll(List.of(officer1, officer2, supervisor, admin));
            System.out.println("Officers seeded successfully. Default password: password123");

            // Assign existing seeded cases (C-001, C-002, C-003) to OFFICER_001 using JdbcTemplate
            // This avoids Hibernate Postgres ENUM mapping issues for 'status'
            try {
                String sql = "UPDATE cases SET created_by = ? WHERE case_id IN ('C-001', 'C-002', 'C-003')";
                jdbcTemplate.update(sql, officer1.getUserId());
                System.out.println("Assigned C-001, C-002, C-003 to OFFICER_001.");
            } catch (Exception e) {
                System.err.println("Could not assign cases: " + e.getMessage());
            }
        }
    }
}
