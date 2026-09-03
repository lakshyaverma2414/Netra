package com.example.CrimeAi.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Service
public class JwtService {

    private static final String SECRET_KEY =
            "CrimeAi_NCRB_Secret_Key_2026_Very_Secure_123456789";

    private static final long EXPIRATION_TIME =
            1000L * 60 * 60;

    private SecretKey getSigningKey() {

        return Keys.hmacShaKeyFor(
                SECRET_KEY.getBytes(StandardCharsets.UTF_8)
        );
    }

    // =========================
    // Generate JWT
    // =========================

    public String generateToken(
            String officerId,
            String role
    ) {

        return Jwts.builder()
                .subject(officerId)
                .claim("role", role)
                .issuedAt(new Date())
                .expiration(
                        new Date(
                                System.currentTimeMillis()
                                        + EXPIRATION_TIME
                        )
                )
                .signWith(getSigningKey())
                .compact();
    }

    // =========================
    // Extract all claims
    // =========================

    private Claims extractAllClaims(String token) {

        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    // =========================
    // Extract Officer ID
    // =========================

    public String extractOfficerId(String token) {

        return extractAllClaims(token)
                .getSubject();
    }

    // =========================
    // Extract Role
    // =========================

    public String extractRole(String token) {

        return extractAllClaims(token)
                .get("role", String.class);
    }

    // =========================
    // Validate JWT
    // =========================

    public boolean isTokenValid(String token) {

        try {

            Claims claims = extractAllClaims(token);

            return claims
                    .getExpiration()
                    .after(new Date());

        } catch (Exception e) {

            return false;
        }
    }
}