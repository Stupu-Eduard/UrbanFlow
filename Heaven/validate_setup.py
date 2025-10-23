#!/usr/bin/env python3
"""
UrbanFlowAI Setup Validation Script
Checks if all components are properly configured
"""

import sys
import subprocess
import json
from pathlib import Path

CHECKS = []
WARNINGS = []
ERRORS = []

def check(name):
    """Decorator to register check functions"""
    def decorator(func):
        CHECKS.append((name, func))
        return func
    return decorator

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_result(status, message):
    """Print check result"""
    symbols = {"pass": "[OK]", "warn": "[WARN]", "fail": "[FAIL]"}
    symbol = symbols.get(status, "[INFO]")
    print(f"{symbol} {message}")

@check("Project Structure")
def check_project_structure():
    """Verify all required directories and files exist"""
    required_files = [
        "api/main.py",
        "api/config.py",
        "api/database.py",
        "api/services.py",
        "api/redis_client.py",
        "api/routing_service.py",
        "api/contracts.py",
        "api/requirements.txt",
        "api/Dockerfile",
        "docker-compose.yml",
        "init-db/01-init.sql"
    ]
    
    required_dirs = [
        "api",
        "init-db",
        "osrm-data",
        "graphhopper-data",
        "graphhopper-config"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not Path(file).is_file():
            missing_files.append(file)
    
    for dir in required_dirs:
        if not Path(dir).is_dir():
            missing_dirs.append(dir)
    
    if missing_files or missing_dirs:
        if missing_files:
            ERRORS.append(f"Missing files: {', '.join(missing_files)}")
        if missing_dirs:
            ERRORS.append(f"Missing directories: {', '.join(missing_dirs)}")
        return False
    
    return True

@check("Python Dependencies")
def check_python_deps():
    """Check if requirements.txt has all necessary packages"""
    req_file = Path("api/requirements.txt")
    if not req_file.exists():
        ERRORS.append("requirements.txt not found")
        return False
    
    required_packages = [
        "fastapi", "uvicorn", "redis", "psycopg2-binary",
        "sqlalchemy", "geoalchemy2", "pydantic", "pydantic-settings",
        "httpx", "python-dotenv", "shapely"
    ]
    
    content = req_file.read_text().lower()
    missing = [pkg for pkg in required_packages if pkg not in content]
    
    if missing:
        ERRORS.append(f"Missing packages in requirements.txt: {', '.join(missing)}")
        return False
    
    return True

@check("Docker Configuration")
def check_docker_config():
    """Verify docker-compose.yml is properly configured"""
    compose_file = Path("docker-compose.yml")
    if not compose_file.exists():
        ERRORS.append("docker-compose.yml not found")
        return False
    
    content = compose_file.read_text()
    required_services = ["redis", "postgres", "osrm", "graphhopper", "api"]
    
    missing = [svc for svc in required_services if f"{svc}:" not in content]
    
    if missing:
        ERRORS.append(f"Missing services in docker-compose.yml: {', '.join(missing)}")
        return False
    
    return True

@check("Python Syntax")
def check_python_syntax():
    """Check all Python files for syntax errors"""
    python_files = list(Path("api").glob("*.py"))
    
    errors = []
    for file in python_files:
        try:
            compile(file.read_text(), str(file), 'exec')
        except SyntaxError as e:
            errors.append(f"{file}: {e}")
    
    if errors:
        ERRORS.extend(errors)
        return False
    
    return True

@check("Import Structure")
def check_imports():
    """Verify critical imports work"""
    import_tests = [
        ("api.config", "Settings"),
        ("api.contracts", "LiveStatusResponse"),
        ("api.contracts", "RouteRequest"),
    ]
    
    # Add api directory to path
    sys.path.insert(0, str(Path("api").resolve()))
    
    errors = []
    for module, attr in import_tests:
        try:
            mod = __import__(module, fromlist=[attr])
            if not hasattr(mod, attr):
                errors.append(f"{module} missing {attr}")
        except ImportError as e:
            errors.append(f"Cannot import {module}: {e}")
    
    if errors:
        WARNINGS.extend(errors)
        WARNINGS.append("Note: Some imports may fail without installed dependencies")
        return True  # Don't fail on this
    
    return True

@check("Docker Availability")
def check_docker_running():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            WARNINGS.append("Docker is not running. Start Docker to continue.")
            return True  # Warning, not error
        return True
    except FileNotFoundError:
        ERRORS.append("Docker is not installed")
        return False
    except subprocess.TimeoutExpired:
        WARNINGS.append("Docker command timed out")
        return True

@check("Code Quality")
def check_code_quality():
    """Check for common code quality issues"""
    issues = []
    
    # Check for TODO/FIXME comments
    python_files = list(Path("api").glob("*.py"))
    for file in python_files:
        content = file.read_text()
        if "# TODO" in content or "# FIXME" in content:
            issues.append(f"{file.name} contains TODO/FIXME comments")
    
    if issues:
        WARNINGS.extend(issues)
    
    return True

def run_checks():
    """Run all validation checks"""
    print_header("UrbanFlowAI Configuration Validator")
    
    passed = 0
    failed = 0
    
    for name, check_func in CHECKS:
        try:
            result = check_func()
            if result:
                print_result("pass", f"{name}: OK")
                passed += 1
            else:
                print_result("fail", f"{name}: FAILED")
                failed += 1
        except Exception as e:
            print_result("fail", f"{name}: ERROR - {e}")
            failed += 1
            ERRORS.append(f"{name}: {str(e)}")
    
    # Print summary
    print_header("Validation Summary")
    print(f"Checks passed: {passed}/{len(CHECKS)}")
    print(f"Checks failed: {failed}/{len(CHECKS)}")
    
    if WARNINGS:
        print("\n[!] WARNINGS:")
        for warning in WARNINGS:
            print(f"  - {warning}")
    
    if ERRORS:
        print("\n[X] ERRORS:")
        for error in ERRORS:
            print(f"  - {error}")
    
    print()
    
    if failed == 0 and not ERRORS:
        print("[SUCCESS] All checks passed! Your setup looks good.")
        print("\nNext steps:")
        print("  1. Run: docker-compose up -d")
        print("  2. Wait for services to start (60-90 seconds)")
        print("  3. Run: curl -X POST http://localhost:8000/api/v1/admin/seed-data")
        print("  4. Run: curl -X POST http://localhost:8000/api/v1/admin/seed-redis")
        print("  5. Test: curl http://localhost:8000/api/v1/status/live")
        return 0
    else:
        print("[FAILED] Some checks failed. Please fix the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_checks())

