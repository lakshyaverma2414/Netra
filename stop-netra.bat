@echo off
echo ===================================================
echo               NETRA SHUTDOWN SYSTEM
echo ===================================================
echo.

echo [1/4] Stopping Llama Server (WSL)...
wsl -e pkill -f llama-server >nul 2>&1

echo [2/4] Stopping Python AI Service (WSL)...
wsl -e pkill -f uvicorn >nul 2>&1

echo [3/4] Stopping Spring Boot (Java)...
:: We use wmic to specifically target the spring boot java process without killing your IDE (like IntelliJ/Eclipse)
wmic process where "commandline like '%%spring-boot%%' and name='java.exe'" call terminate >nul 2>&1
wmic process where "commandline like '%%CrimeAi%%' and name='java.exe'" call terminate >nul 2>&1

echo [4/4] Stopping React Frontend (Node)...
:: Target specifically the vite node process
wmic process where "commandline like '%%vite%%' and name='node.exe'" call terminate >nul 2>&1

echo.
echo Cleaning up terminal windows...
taskkill /F /FI "WindowTitle eq Llama AI Server*" /T >nul 2>&1
taskkill /F /FI "WindowTitle eq Python FastAPI*" /T >nul 2>&1
taskkill /F /FI "WindowTitle eq Spring Boot*" /T >nul 2>&1
taskkill /F /FI "WindowTitle eq React UI*" /T >nul 2>&1

echo.
echo ===================================================
echo All NETRA services have been successfully stopped!
echo ===================================================
timeout /t 3
