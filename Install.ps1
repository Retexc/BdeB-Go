# Define project directory
$installPath = "$env:ProgramFiles\BdeB-GTFS"

# 1️⃣ Ensure the target directory exists
if (!(Test-Path $installPath)) {
    New-Item -Path $installPath -ItemType Directory -Force
}

# 2️⃣ Install Python if not installed
if (-Not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Output "Installing Python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
    Start-Process -FilePath "$env:TEMP\python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
}

# 3️⃣ Clone or update GitHub repository
if (!(Test-Path "$installPath\.git")) {
    Write-Output "Cloning repository..."
    git clone https://github.com/Retexc/BdeB-GTFS.git $installPath
} else {
    Write-Output "Updating repository..."
    Set-Location -Path $installPath
    git pull
}

# 4️⃣ Install dependencies
Write-Output "Installing Python dependencies..."
Set-Location -Path $installPath
python -m pip install --upgrade pip
# Define the dependencies directly in the script
$dependencies = @(
    "flask",
    "tkcalendar",
    "pillow",
    "requests",
    "google-transit",
    "protobuf"
)

# Install each dependency one by one
foreach ($package in $dependencies) {
    Write-Output "Installing $package..."
    python -m pip install --no-cache-dir $package
    if ($LASTEXITCODE -ne 0) {
        Write-Output "❌ Failed to install $package"
        exit 1
    }
}
Write-Output "✅ All dependencies installed successfully!"

# 5️⃣ Create Desktop Shortcut
$shortcutPath = "$env:Public\Desktop\BdeB-GTFS.lnk"
$targetPath = "C:\Windows\System32\cmd.exe"
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.Arguments = "/k cd `"$installPath`" & python app.py"
$shortcut.Save()

Write-Output "Installation Complete!"
