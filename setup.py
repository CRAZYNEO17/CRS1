import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    try:
        # Create virtual environment if it doesn't exist
        if not os.path.exists("venv"):
            print("Creating virtual environment...")
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        
        # Activate virtual environment and install requirements
        if sys.platform == "win32":
            python = ".\\venv\\Scripts\\python.exe"
            pip = ".\\venv\\Scripts\\pip.exe"
        else:
            python = "./venv/bin/python"
            pip = "./venv/bin/pip"
        
        print("Upgrading pip...")
        subprocess.check_call([pip, "install", "--upgrade", "pip"])
        
        # Install GPS dependencies first
        print("Installing GPS dependencies...")
        if sys.platform == "win32":
            subprocess.check_call([pip, "install", "gpsd-py3==0.3.0", "pyserial"])
        else:
            subprocess.check_call([pip, "install", "gpsd-py3==0.3.0"])
        
        print("Installing requirements...")
        subprocess.check_call([pip, "install", "-r", "requirements.txt"])
        
        print("\nSetup completed successfully!")
        print("To activate the virtual environment:")
        if sys.platform == "win32":
            print("Run: .\\venv\\Scripts\\activate")
        else:
            print("Run: source venv/bin/activate")
            
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()