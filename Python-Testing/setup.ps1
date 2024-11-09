# Colored output
function Write-ColoredMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Check-PythonVersion {
    try {
        $pythonVersion = (python --version).Split(" ")[1]
        $requiredVersion = "3.13.0"
        
        if ([version]$pythonVersion -lt [version]$requiredVersion) {
            Write-ColoredMessage "Error: Python version $requiredVersion or higher is required. Found version $pythonVersion" "Red"
            exit 1
        }
    }
    catch {
        Write-ColoredMessage "Error: Python is not installed or not in PATH" "Red"
        exit 1
    }
}

function Setup-VirtualEnv {
    Write-ColoredMessage "Setting up virtual environment..." "Yellow"
    
    # Remove existing venv if it exists
    if (Test-Path "WindViz") {
        Write-ColoredMessage "Removing existing virtual environment..." "Yellow"
        Remove-Item -Recurse -Force "WindViz"
    }
    
    # Create new virtual environment
    python -m venv WindViz
    if ($LASTEXITCODE -ne 0) {
        Write-ColoredMessage "Error: Failed to create virtual environment" "Red"
        exit 1
    }
    
    # Activate venv
    & .\WindViz\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-ColoredMessage "Error: Failed to activate virtual environment" "Red"
        exit 1
    }
    
    Write-ColoredMessage "Virtual environment created and activated successfully." "Green"
}

function Install-Dependencies {
    Write-ColoredMessage "Installing required packages..." "Yellow"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-ColoredMessage "Error: Failed to upgrade pip" "Red"
        exit 1
    }
    
    # Install requirements
    if (Test-Path "requirements.txt") {
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-ColoredMessage "Error: Failed to install dependencies" "Red"
            exit 1
        }
        Write-ColoredMessage "Dependencies installed successfully." "Green"
    }
    else {
        Write-ColoredMessage "Error: requirements.txt not found." "Red"
        exit 1
    }
}

function Main {
    Write-ColoredMessage "Starting WindViz LU setup..." "Yellow"
    
    Check-PythonVersion
    Setup-VirtualEnv
    Install-Dependencies
    
    Write-ColoredMessage "`nSetup completed successfully!" "Green"
    Write-ColoredMessage "`nTo use WindViz LU:" "Yellow"
    Write-ColoredMessage "1. Make sure you're in the virtual environment (look for '(WindViz)' in your terminal)" "Yellow"
    Write-ColoredMessage "2. Run 'python main.py' to start the application" "Yellow"
    Write-ColoredMessage "`nIf you close your terminal, reactivate the virtual environment with:" "Yellow"
    Write-ColoredMessage "    .\WindViz\Scripts\Activate.ps1" "Yellow"
}


$ErrorActionPreference = "Stop"

try {
    Main
}
catch {
    Write-ColoredMessage "`nError: Setup failed - $($_.Exception.Message)" "Red"
    exit 1
}