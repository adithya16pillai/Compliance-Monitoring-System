#!/usr/bin/env python3
"""
Compliance Monitoring System Startup Script

This script helps start the complete system with proper environment setup.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'sqlalchemy', 
        'pandas', 'requests', 'openai', 'anthropic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    if missing_packages:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['uploads', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Directory '{dir_name}' ready")

def check_env_file():
    """Check and create .env file if needed"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found, creating default...")
        with open('.env', 'w') as f:
            f.write("""# LLM API Keys (Optional - add your keys for enhanced analysis)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=sqlite:///./compliance.db

# App Settings
DEBUG=True
MAX_FILE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=pdf,docx,txt
""")
        print("✅ Created default .env file")
    else:
        print("✅ .env file exists")

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])

def start_streamlit_app():
    """Start the Streamlit application"""
    print("🌟 Starting Streamlit application...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "ui/streamlit_app.py"
    ])

def wait_for_api(timeout=30):
    """Wait for API to be ready"""
    print("⏳ Waiting for API to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:8000/health", timeout=1)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except:
            pass
        time.sleep(1)
    
    print("❌ API failed to start within timeout")
    return False

def main():
    """Main startup function"""
    print("🔍 Compliance Monitoring System Startup")
    print("=" * 50)
    
    # Pre-flight checks
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        print("\n⚠️  Please install missing dependencies first:")
        print("pip install -r requirements.txt")
        return 1
    
    # Setup
    create_directories()
    check_env_file()
    
    print("\n🚀 Starting services...")
    
    # Start API server
    api_process = start_api_server()
    
    # Wait for API to be ready
    if not wait_for_api():
        api_process.terminate()
        return 1
    
    # Start Streamlit app
    streamlit_process = start_streamlit_app()
    
    print("\n✅ System started successfully!")
    print("📊 Streamlit UI: http://localhost:8501")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep both processes running
        api_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        api_process.terminate()
        streamlit_process.terminate()
        print("✅ Services stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())