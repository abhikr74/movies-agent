#!/usr/bin/env python3
"""
Movie Recommendation System Setup Script
Automated setup for the movie recommendation system
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def setup_environment():
    """Set up environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        print("📝 Creating environment file...")
        env_example.rename(env_file)
        print("✅ Environment file created")
    elif env_file.exists():
        print("✅ Environment file already exists")
    else:
        print("⚠️ No .env.example found, creating basic .env")
        with open(".env", "w") as f:
            f.write("DATABASE_URL=sqlite:///./data/processed/movies.db\n")
            f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("API_HOST=0.0.0.0\n")
            f.write("API_PORT=8000\n")

def setup_data():
    """Initialize database and load data"""
    return run_command("python scripts/setup_data.py", "Setting up database and loading movie data")

def main():
    """Main setup function"""
    print("🎬 Movie Recommendation System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Setup data
    if not setup_data():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the API server: python scripts/run_server.py")
    print("2. Open browser to: http://localhost:8000/docs")
    print("3. Run demo app: streamlit run streamlit_demo.py")
    print("4. Run evaluation: python scripts/run_evaluation.py")
    
    # Optional Ollama setup
    print("\n💡 Optional: For enhanced responses, install Ollama:")
    print("   1. Download from: https://ollama.ai")
    print("   2. Run: ollama pull llama3.1:8b")
    print("   3. Start: ollama serve")

if __name__ == "__main__":
    main()