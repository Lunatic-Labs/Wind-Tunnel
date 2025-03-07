import os
import subprocess
import platform

def run_setup():
    system = platform.system()
    if system == "Windows":
        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "setup.ps1"], check=True)
    elif system in ("Linux", "Darwin"):  # Darwin is macOS
        subprocess.run(["bash", "setup.sh"], check=True)
    else:
        print(f"Unsupported OS: {system}")

if __name__ == "__main__":
    run_setup()