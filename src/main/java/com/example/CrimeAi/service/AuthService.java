package com.example.CrimeAi.service;

import com.example.CrimeAi.dto.LoginRequest;
import com.example.CrimeAi.dto.LoginResponse;
import com.example.CrimeAi.dto.UserResponse;
import com.example.CrimeAi.entity.User;
import com.example.CrimeAi.repository.UserRepository;
import com.example.CrimeAi.security.JwtService;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtService jwtService
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public LoginResponse login(LoginRequest request) {

        User user = userRepository
                .findByUsername(request.getOfficerId())
                .orElse(null);

        if (user == null) {
            return new LoginResponse(
                    false,
                    "Invalid officer ID or password",
                    null,
                    null
            );
        }

        boolean passwordMatches =
                passwordEncoder.matches(
                        request.getPassword(),
                        user.getPassword()
                );

        if (!passwordMatches) {
            return new LoginResponse(
                    false,
                    "Invalid officer ID or password",
                    null,
                    null
            );
        }

        // Temporary CAPTCHA validation
        if (!"Q8x2P".equalsIgnoreCase(request.getCaptcha())) {
            return new LoginResponse(
                    false,
                    "Invalid captcha",
                    null,
                    null
            );
        }

        String token = jwtService.generateToken(
                user.getUsername(),
                user.getRole()
        );

        UserResponse userResponse = new UserResponse(
                user.getUsername(),
                user.getName(),
                user.getRole()
        );

        return new LoginResponse(
                true,
                "Login successful",
                token,
                userResponse
        );
    }
    public String generateTestPasswordHash() {
        return passwordEncoder.encode("password123");
    }
}