# Set project installation path
$installPath = "$env:ProgramFiles\BdeB-GTFS"

# 1️⃣ Create install directory if needed
if (!(Test-Path $installPath)) {
    New-Item -Path $installPath -ItemType Directory -Force
}

# 2️⃣ Install Python if not installed
if (-Not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Output "Installing Python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
    Start-Process -FilePath "$env:TEMP\python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
}

# 3️⃣ Clone or update the project from GitHub
if (!(Test-Path "$installPath\.git")) {
    Write-Output "Cloning repository..."
    git clone https://github.com/Retexc/BdeB-GTFS.git $installPath
} else {
    Write-Output "Updating repository..."
    Set-Location -Path $installPath
    git pull
}

# 4️⃣ Install Python dependencies manually (no requirements.txt)
Write-Output "Installing Python dependencies..."
Set-Location -Path $installPath

# Upgrade pip
python -m pip install --upgrade pip

# List of dependencies
$dependencies = @(
    "flask",
    "tkcalendar",
    "pillow",
    "requests",
    "protobuf",
    "gtfs-realtime-bindings"
)

foreach ($package in $dependencies) {
    Write-Output "Installing $package..."
    python -m pip install --no-cache-dir $package
    if ($LASTEXITCODE -ne 0) {
        Write-Output "❌ Failed to install $package"
        exit 1
    }
}
Write-Output "✅ All dependencies installed."

# 5️⃣ Create a Desktop Shortcut
$shortcutPath = "$env:Public\Desktop\BdeB-GTFS.lnk"
$targetPath = "C:\Windows\System32\cmd.exe"
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.Arguments = "/k cd `"$installPath`" & python app.py"
$shortcut.Save()

Write-Output "✅ Installation Complete!"
