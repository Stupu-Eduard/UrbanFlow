# UrbanFlowAI - Windows Setup Guide

## 🚨 **IMPORTANT: Docker Required**

Your system analysis shows that **Docker is not installed**. You must install Docker Desktop before running this project.

---

## 📥 **Step 1: Install Docker Desktop**

### Download & Install

1. **Download Docker Desktop for Windows:**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - **Minimum Requirements:**
     - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
     - OR Windows 11 64-bit
     - WSL 2 feature enabled
     - 4GB RAM (8GB+ recommended)

2. **Install Docker Desktop:**
   - Run the downloaded installer
   - Follow the installation wizard
   - **Enable WSL 2** when prompted (recommended)
   - Restart your computer when installation completes

3. **Start Docker Desktop:**
   - Launch Docker Desktop from Start Menu
   - Wait for the Docker Engine to start (icon in system tray)
   - You'll see "Docker Desktop is running" when ready

4. **Verify Installation:**
   ```powershell
   docker --version
   docker compose version
   ```
   
   Expected output:
   ```
   Docker version 24.x.x
   Docker Compose version v2.x.x
   ```

---

## 🚀 **Step 2: Run UrbanFlowAI**

Once Docker is installed and running:

### Option A: Use the Quickstart Script

```powershell
.\quickstart.bat
```

### Option B: Manual Commands (PowerShell)

```powershell
# 1. Start all services (note: docker compose, not docker-compose)
docker compose up -d

# 2. Wait 60-90 seconds for services to start
Start-Sleep -Seconds 60

# 3. Seed the database
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/admin/seed-data"

# 4. Seed Redis
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/admin/seed-redis"

# 5. Test the API
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/status/live"

# 6. Check health
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

---

## 📝 **PowerShell Command Reference**

### Docker Commands

```powershell
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f api

# Check status
docker compose ps

# Restart a service
docker compose restart api
```

### API Testing (PowerShell-friendly)

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Get live status
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/status/live" | ConvertTo-Json -Depth 10

# Seed database
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/admin/seed-data"

# Seed Redis
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/admin/seed-redis"

# Check Redis status
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/redis-status"
```

### Route Calculation Example

```powershell
# Citizen mode route
$body = @{
    start = @{
        latitude = 40.7489
        longitude = -73.9852
    }
    end = @{
        latitude = 40.7599
        longitude = -73.9762
    }
    mode = "citizen"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/route/calculate" `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10
```

```powershell
# Emergency mode route
$body = @{
    start = @{
        latitude = 40.7489
        longitude = -73.9852
    }
    end = @{
        latitude = 40.7599
        longitude = -73.9762
    }
    mode = "emergency"
    vehicle_id = "truck_01"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/route/calculate" `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10
```

---

## 🔧 **Troubleshooting**

### Issue: "docker: command not found"
**Solution:** Docker Desktop is not installed or not in PATH.
- Restart PowerShell after installing Docker
- Ensure Docker Desktop is running (check system tray icon)
- Try: `& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' --version`

### Issue: "docker compose: command not found"
**Solution:** You have an old Docker version.
- Update Docker Desktop to latest version
- Alternatively, use legacy command: `docker-compose` (with hyphen)

### Issue: "Cannot connect to Docker daemon"
**Solution:** Docker Desktop is not running.
- Start Docker Desktop from Start Menu
- Wait for "Docker Desktop is running" notification
- Check system tray for Docker whale icon

### Issue: "WSL 2 installation is incomplete"
**Solution:** Enable WSL 2 feature.
```powershell
# Run as Administrator
wsl --install
# Restart computer
```

### Issue: "Invoke-RestMethod: Unable to connect"
**Solution:** Services are not ready yet.
- Wait longer (services can take 90+ seconds to start)
- Check if containers are running: `docker compose ps`
- Check logs: `docker compose logs api`

---

## ✅ **Pre-Flight Checklist**

Before running UrbanFlowAI:

- [ ] Docker Desktop installed
- [ ] Docker Desktop is running (green icon in system tray)
- [ ] `docker --version` works
- [ ] `docker compose version` works
- [ ] At least 8GB free RAM
- [ ] At least 10GB free disk space
- [ ] Ports 5432, 6379, 5000, 8000, 8989 are free

Check port availability:
```powershell
# Check if ports are in use
Get-NetTCPConnection -LocalPort 8000,5432,6379,5000,8989 -ErrorAction SilentlyContinue
# If this returns nothing, ports are free. Good!
```

---

## 🌐 **Access Points (After Setup)**

| Service | URL |
|---------|-----|
| API Documentation | http://localhost:8000/docs |
| Alternative Docs | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Live Status | http://localhost:8000/api/v1/status/live |

---

## 📦 **What Gets Installed**

When you run `docker compose up -d`, these containers start:

1. **Redis** (port 6379) - Real-time data store
2. **PostgreSQL + PostGIS** (port 5432) - Persistent database
3. **OSRM** (port 5000) - Fast routing engine
4. **GraphHopper** (port 8989) - Smart routing engine
5. **UrbanFlowAI API** (port 8000) - Your backend application

Total disk space needed: ~3-5GB

---

## 🎯 **Quick Start Checklist**

1. **Install Docker Desktop**
   - Download from docker.com
   - Install with WSL 2
   - Start Docker Desktop
   - Verify: `docker --version`

2. **Clone/Navigate to Project**
   ```powershell
   cd D:\Heaven
   ```

3. **Start Services**
   ```powershell
   docker compose up -d
   ```

4. **Wait for Services**
   ```powershell
   Start-Sleep -Seconds 90
   ```

5. **Initialize Data**
   ```powershell
   Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/admin/seed-data"
   Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/admin/seed-redis"
   ```

6. **Verify**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8000/health"
   ```

7. **Open Browser**
   - Navigate to: http://localhost:8000/docs
   - Try the interactive API documentation!

---

## 💡 **Tips for Windows Users**

### Use PowerShell, Not CMD
PowerShell has better command support. Open PowerShell as Administrator for best results.

### Docker Desktop Settings
- **Resources → Advanced:** Increase CPU/Memory if services are slow
- **Resources → WSL Integration:** Enable for your WSL distributions
- **General:** Enable "Use Docker Compose V2"

### Port Conflicts
If you get port binding errors:
```powershell
# Find what's using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Kill the process or change port in docker-compose.yml
```

### Performance
- Use WSL 2 backend (faster than Hyper-V)
- Keep project files on the native Windows filesystem for Docker Desktop
- Close other heavy applications when running all services

---

## 🔗 **Useful Resources**

- Docker Desktop Documentation: https://docs.docker.com/desktop/windows/
- WSL 2 Setup: https://docs.microsoft.com/en-us/windows/wsl/install
- Docker Compose Reference: https://docs.docker.com/compose/

---

## ⚡ **Alternative: Use Python Locally (Without Docker)**

If you want to run just the API without Docker:

```powershell
# Install Python dependencies
cd api
pip install -r requirements.txt

# Start just Redis and PostgreSQL in Docker
docker compose up -d redis postgres

# Set environment variables
$env:REDIS_HOST = "localhost"
$env:POSTGRES_HOST = "localhost"
$env:OSRM_URL = "http://localhost:5000"
$env:GRAPHHOPPER_URL = "http://localhost:8989"

# Run the API directly
python main.py
```

This is useful for development but not recommended for production.

---

## 📞 **Need Help?**

If you're still having issues:

1. Check Docker Desktop is running (system tray icon)
2. Run: `docker compose logs api`
3. Check: `docker compose ps`
4. Verify: `docker info`
5. Review: CONFIGURATION_REPORT.md

**Common error messages and solutions are in the Troubleshooting section above.**

---

**Ready to install Docker? Start with Step 1 above! 🚀**


