@echo off
REM UrbanFlowAI Quick Start Script for Windows
REM This script sets up and starts the entire system

echo.
echo 🧠 UrbanFlowAI - Quick Start
echo ==============================
echo.

REM Check if Docker is installed
where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    echo.
    echo See WINDOWS_SETUP_GUIDE.md for detailed instructions.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and wait for it to fully initialize.
    echo Look for the Docker whale icon in your system tray.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Step 1: Start services (use modern 'docker compose' syntax)
echo Starting all services...
docker compose up -d 2>nul
if errorlevel 1 (
    echo Trying legacy docker-compose command...
    docker-compose up -d
    if errorlevel 1 (
        echo [ERROR] Failed to start services.
        echo Please check docker-compose.yml for errors.
        pause
        exit /b 1
    )
)

echo.
echo Waiting for services to be healthy (this may take 60-90 seconds)...
timeout /t 10 /nobreak >nul

REM Wait for API to be ready
set MAX_RETRIES=30
set RETRY_COUNT=0

:wait_loop
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 goto api_ready

set /a RETRY_COUNT+=1
if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo ❌ API failed to start. Check logs with: docker-compose logs api
    exit /b 1
)

echo Waiting for API... (attempt %RETRY_COUNT%/%MAX_RETRIES%)
timeout /t 3 /nobreak >nul
goto wait_loop

:api_ready
echo [OK] All services are running
echo.

REM Step 2: Initialize database (using PowerShell for HTTP requests)
echo Initializing database with sample data...
powershell -Command "try { Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/v1/admin/seed-data' -ErrorAction Stop | Out-Null; Write-Host '[OK] Database seeded' } catch { Write-Host '[WARN] Database seeding failed -' $_.Exception.Message }"

REM Step 3: Initialize Redis
echo Initializing Redis with sample real-time data...
powershell -Command "try { Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/v1/admin/seed-redis' -ErrorAction Stop | Out-Null; Write-Host '[OK] Redis seeded' } catch { Write-Host '[WARN] Redis seeding failed -' $_.Exception.Message }"
echo.

REM Step 4: Test the API
echo Testing API...
powershell -Command "try { $result = Invoke-RestMethod -Uri 'http://localhost:8000/health' -ErrorAction Stop; if ($result.status -eq 'healthy') { Write-Host '[OK] API is healthy' } else { Write-Host '[WARN] API status:' $result.status } } catch { Write-Host '[ERROR] API not responding' }"
echo.

REM Success message
echo ==============================
echo UrbanFlowAI is ready!
echo ==============================
echo.
echo Access points:
echo    API:           http://localhost:8000
echo    Documentation: http://localhost:8000/docs
echo    Health:        http://localhost:8000/health
echo.
echo PowerShell test commands:
echo    Get live status:
echo      Invoke-RestMethod -Uri http://localhost:8000/api/v1/status/live
echo.
echo    View logs:
echo      docker compose logs -f api
echo.
echo    Stop system:
echo      docker compose down
echo.
echo Next steps:
echo    1. Open http://localhost:8000/docs in your browser
echo    2. Try the '/api/v1/status/live' endpoint
echo    3. Try the '/api/v1/route/calculate' endpoint
echo.
echo For more PowerShell examples, see WINDOWS_SETUP_GUIDE.md
echo.
echo Happy coding!
echo.

pause

