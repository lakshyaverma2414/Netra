package com.example.CrimeAi.config;

import com.example.CrimeAi.entity.User;
import com.example.CrimeAi.repository.UserRepository;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class DataInitializer {

    @Bean
    CommandLineRunner initializeAdmin(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder
    ) {

        return args -> {

            if (userRepository.findByUsername("admin").isEmpty()) {

                User admin = new User();

                admin.setUsername("admin");
                admin.setName("Investigation Officer");
                admin.setPassword(
                        passwordEncoder.encode("admin")
                );
                admin.setRole("ADMIN");

                userRepository.save(admin);

                System.out.println(
                        "Default admin user created."
                );
            }
        };
    }
}