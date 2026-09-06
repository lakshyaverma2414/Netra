package com.example.CrimeAi.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;

    public JwtAuthenticationFilter(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        String requestPath = request.getServletPath();

        System.out.println();
        System.out.println("==========================================");
        System.out.println("JWT FILTER");
        System.out.println("Request : " + request.getMethod() + " " + requestPath);
        System.out.println("==========================================");

        // ==========================================
        // LOGIN ENDPOINT
        // ==========================================

        if (requestPath.equals("/api/auth/login")) {

            System.out.println(
                    "Login endpoint - JWT validation skipped"
            );

            filterChain.doFilter(request, response);
            return;
        }

        // ==========================================
        // GET AUTHORIZATION HEADER
        // ==========================================

        String authHeader = request.getHeader("Authorization");

        System.out.println(
                "Authorization Header = " + authHeader
        );

        // ==========================================
        // NO TOKEN
        // ==========================================

        if (authHeader == null
                || authHeader.isBlank()
                || !authHeader.startsWith("Bearer ")) {

            System.out.println(
                    "No valid Bearer token found"
            );

            filterChain.doFilter(request, response);
            return;
        }

        // ==========================================
        // EXTRACT TOKEN
        // ==========================================

        String token = authHeader.substring(7).trim();

        if (token.isBlank()) {

            System.out.println(
                    "Bearer token is empty"
            );

            filterChain.doFilter(request, response);
            return;
        }

        try {

            // ==========================================
            // EXTRACT OFFICER ID
            // ==========================================

            String officerId =
                    jwtService.extractOfficerId(token);

            // ==========================================
            // EXTRACT ROLE
            // ==========================================

            String role =
                    jwtService.extractRole(token);

            System.out.println(
                    "JWT Officer = " + officerId
            );

            System.out.println(
                    "JWT Role = " + role
            );

            // ==========================================
            // VALIDATE TOKEN
            // ==========================================

            boolean validToken =
                    jwtService.isTokenValid(token);

            System.out.println(
                    "JWT Valid = " + validToken
            );

            // ==========================================
            // CREATE AUTHENTICATION
            // ==========================================

            if (officerId != null
                    && !officerId.isBlank()
                    && validToken
                    && SecurityContextHolder
                    .getContext()
                    .getAuthentication() == null) {

                // --------------------------------------
                // SAFE ROLE HANDLING
                // --------------------------------------

                String authorityRole = role;

                if (authorityRole == null
                        || authorityRole.isBlank()) {

                    authorityRole = "OFFICER";
                }

                // Remove ROLE_ if JWT already contains it
                if (authorityRole.startsWith("ROLE_")) {
                    authorityRole =
                            authorityRole.substring(5);
                }

                String authority =
                        "ROLE_" + authorityRole;

                System.out.println(
                        "Spring Security Authority = "
                                + authority
                );

                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                officerId,
                                null,
                                List.of(
                                        new SimpleGrantedAuthority(
                                                authority
                                        )
                                )
                        );

                // --------------------------------------
                // SET SECURITY CONTEXT
                // --------------------------------------

                SecurityContextHolder
                        .getContext()
                        .setAuthentication(
                                authentication
                        );

                System.out.println(
                        "JWT Authentication SUCCESS"
                );

                System.out.println(
                        "Authenticated Officer = "
                                + authentication.getName()
                );

                System.out.println(
                        "Authorities = "
                                + authentication.getAuthorities()
                );

            } else {

                System.out.println(
                        "JWT Authentication NOT CREATED"
                );

                if (officerId == null
                        || officerId.isBlank()) {

                    System.out.println(
                            "Reason: Officer ID is null/empty"
                    );
                }

                if (!validToken) {

                    System.out.println(
                            "Reason: JWT token is invalid"
                    );
                }

                if (SecurityContextHolder
                        .getContext()
                        .getAuthentication() != null) {

                    System.out.println(
                            "Reason: Authentication already exists"
                    );
                }
            }

        } catch (Exception e) {

            System.out.println();
            System.out.println(
                    "JWT Authentication FAILED"
            );

            System.out.println(
                    "Error = " + e.getMessage()
            );

            e.printStackTrace();

            // Do not stop the filter chain here.
            // Spring Security will decide whether
            // the endpoint requires authentication.
        }

        // ==========================================
        // CONTINUE REQUEST
        // ==========================================

        filterChain.doFilter(request, response);
    }
}