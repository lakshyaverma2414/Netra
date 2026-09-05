@echo off
echo ===================================================
echo               NETRA STARTUP SYSTEM
echo ===================================================
echo.

:: Ensure we are in the correct directory (D:\NETRA\SIH2026)
cd /d "D:\NETRA\SIH2026"

:: 1. START LLAMA SERVER (WSL)
echo [1/4] Starting Llama Server on port 8081 (via WSL)...
start "Llama AI Server" wsl bash -ic "/home/lakshya/miniconda3/bin/llama-server --port 8081 -m /mnt/d/AI/Models/Qwen3-4B-Instruct-2507/Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf --jinja -ngl 99 -fa -c 8192; exec bash"

:: Wait 3 seconds
timeout /t 3 /nobreak >nul

:: 2. START PYTHON AI SERVICE (WSL, in ai-service directory)
echo [2/4] Starting Python AI Service in WSL...
start "Python FastAPI" wsl --cd /mnt/d/NETRA/SIH2026/ai-service bash -ic "uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload; exec bash"

:: Wait 2 seconds
timeout /t 2 /nobreak >nul

:: 3. START SPRING BOOT (PowerShell, in root directory)
echo [3/4] Starting Spring Boot Gateway...
start "Spring Boot" powershell -NoExit -Command "Set-Location -Path 'D:\NETRA\SIH2026'; .\mvnw.cmd spring-boot:run"

:: Wait 6 seconds to let Spring Boot initialize
timeout /t 6 /nobreak >nul

:: 4. START REACT FRONTEND (PowerShell, in root directory)
echo [4/4] Starting React Frontend...
start "React UI" powershell -NoExit -Command "Set-Location -Path 'D:\NETRA\SIH2026'; npm run dev"

echo.
echo ===================================================
echo All services are launching in their correct environments!
echo ===================================================
pause
