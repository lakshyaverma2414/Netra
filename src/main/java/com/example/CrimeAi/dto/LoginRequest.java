package com.example.CrimeAi.dto;

import jakarta.validation.constraints.NotBlank;

public class LoginRequest {

    @NotBlank(message = "Officer ID is required")
    private String officerId;

    @NotBlank(message = "Password is required")
    private String password;

    @NotBlank(message = "Captcha is required")
    private String captcha;

    private boolean rememberDevice;

    public LoginRequest() {
    }

    public String getOfficerId() {
        return officerId;
    }

    public void setOfficerId(String officerId) {
        this.officerId = officerId;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getCaptcha() {
        return captcha;
    }

    public void setCaptcha(String captcha) {
        this.captcha = captcha;
    }

    public boolean isRememberDevice() {
        return rememberDevice;
    }

    public void setRememberDevice(boolean rememberDevice) {
        this.rememberDevice = rememberDevice;
    }
}