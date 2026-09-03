package com.example.CrimeAi.dto;

public class UserResponse {

    private String officerId;
    private String name;
    private String role;

    public UserResponse() {
    }

    public UserResponse(String officerId, String name, String role) {
        this.officerId = officerId;
        this.name = name;
        this.role = role;
    }

    public String getOfficerId() {
        return officerId;
    }

    public void setOfficerId(String officerId) {
        this.officerId = officerId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }
}