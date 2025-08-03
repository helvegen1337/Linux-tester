# 🐧 Linux Training Platform - Windows Installer
# Автоматическая установка интерактивного тренажера Linux

param(
    [string]$InstallPath = "$env:USERPROFILE\.local\share\linux-training"
)

# Конфигурация
$RepoUrl = "https://github.com/YOUR_USERNAME/linux-training-platform.git"
$ScriptName = "linux-training"

# Цвета для консоли
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header {
    Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║ 🐧 Linux Interactive Training Platform          ║" -ForegroundColor Magenta  
    Write-Host "║ Установщик для Windows                          ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ Ошибка: $Message" -ForegroundColor Red
    exit 1
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Проверка зависимостей
function Test-Dependencies {
    Write-Info "Проверка зависимостей..."
    
    # Проверка Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python не найден"
        }
        Write-Success "Python найден: $pythonVersion"
    }
    catch {
        Write-Error "Python не найден. Установите Python 3.6 или новее с python.org"
    }
    
    # Проверка Git
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Git не найден"
        }
        Write-Success "Git найден: $gitVersion"
    }
    catch {
        Write-Error "Git не найден. Установите Git с git-scm.com"
    }
    
    # Проверка версии Python
    try {
        $versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Версия Python слишком старая"
        }
    }
    catch {
        Write-Error "Требуется Python 3.6 или новее"
    }
}

# Получение директории установки
function Get-InstallDirectory {
    Write-ColorText "📁 Выберите директорию для установки:" "Cyan"
    Write-Host "   Нажмите Enter для установки в: " -NoNewline
    Write-Host $InstallPath -ForegroundColor Green
    Write-Host "   Или введите свой путь:"
    
    $userInput = Read-Host
    
    if (-not [string]::IsNullOrWhiteSpace($userInput)) {
        $script:InstallPath = $userInput
    }
    
    Write-Info "Директория установки: $InstallPath"
    return $InstallPath
}

# Установка файлов
function Install-Files {
    param([string]$TargetPath)
    
    Write-Info "Создание директории установки..."
    
    # Создаем директорию если её нет
    if (-not (Test-Path $TargetPath)) {
        try {
            New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
        }
        catch {
            Write-Error "Не удалось создать директорию: $TargetPath"
        }
    }
    
    # Клонируем или обновляем репозиторий
    if (Test-Path "$TargetPath\.git") {
        Write-Warning "Директория уже содержит git репозиторий. Обновляем..."
        Set-Location $TargetPath
        try {
            git pull origin main
            if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
        }
        catch {
            Write-Error "Не удалось обновить репозиторий"
        }
    }
    else {
        Write-Info "Загрузка проекта из GitHub..."
        try {
            git clone $RepoUrl $TargetPath
            if ($LASTEXITCODE -ne 0) { throw "Git clone failed" }
        }
        catch {
            Write-Error "Не удалось клонировать репозиторий. Проверьте URL: $RepoUrl"
        }
    }
    
    Write-Success "Проект успешно загружен"
}

# Создание batch файла для запуска
function New-Launcher {
    param([string]$InstallDir)
    
    Write-Info "Создание launcher скрипта..."
    
    # Создаем batch файл в директории пользователя
    $launcherDir = "$env:USERPROFILE\bin"
    if (-not (Test-Path $launcherDir)) {
        New-Item -ItemType Directory -Path $launcherDir -Force | Out-Null
    }
    
    $launcherPath = "$launcherDir\$ScriptName.bat"
    
    $batchContent = @"
@echo off
cd /d "$InstallDir"
python artix_training.py %*
"@
    
    try {
        Set-Content -Path $launcherPath -Value $batchContent -Encoding UTF8
        Write-Success "Launcher создан: $launcherPath"
        
        # Проверяем PATH
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($userPath -notlike "*$launcherDir*") {
            Write-Warning "Директория $launcherDir не в PATH"
            Write-Host "Добавляем в PATH пользователя..." -ForegroundColor Yellow
            
            try {
                $newPath = "$userPath;$launcherDir"
                [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
                Write-Success "PATH обновлен. Перезапустите терминал для применения изменений."
            }
            catch {
                Write-Warning "Не удалось обновить PATH автоматически"
                Write-Host "Добавьте вручную в PATH: $launcherDir" -ForegroundColor Yellow
            }
        }
    }
    catch {
        Write-Error "Не удалось создать launcher: $_"
    }
}

# Тестирование установки
function Test-Installation {
    param([string]$InstallDir)
    
    Write-Info "Тестирование установки..."
    
    Set-Location $InstallDir
    
    # Проверка JSON файлов
    try {
        python -c "import json; json.load(open('training_data.json'))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Файлы данных корректны"
        } else {
            throw "JSON validation failed"
        }
    }
    catch {
        Write-Error "Проблема с файлами данных"
    }
    
    # Проверка основного скрипта
    try {
        python -c "exec(open('artix_training.py').read().replace('main()', 'pass'))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Основной скрипт корректен"
        } else {
            Write-Warning "Возможны проблемы с основным скриптом"
        }
    }
    catch {
        Write-Warning "Не удалось протестировать основной скрипт"
    }
}

# Финальная информация
function Show-CompletionInfo {
    param([string]$InstallDir)
    
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║ 🎉 Установка успешно завершена!                 ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-ColorText "📍 Местоположение: $InstallDir" "Cyan"
    Write-ColorText "🚀 Запуск: $ScriptName" "Cyan"
    Write-ColorText "🔧 Прямой запуск: python `"$InstallDir\artix_training.py`"" "Cyan"
    Write-Host ""
    Write-ColorText "💡 Полезные команды:" "Yellow"
    Write-Host "   • $ScriptName - запуск тренажера" -ForegroundColor Green
    Write-Host "   • cd `"$InstallDir`" && git pull - обновление" -ForegroundColor Green
    Write-Host ""
    Write-ColorText "📚 Документация: $InstallDir\README.md" "Magenta"
    Write-ColorText "🔍 Техдокументация: $InstallDir\TECHNICAL_DOCS.md" "Magenta"
    Write-Host ""
    Write-ColorText "⚠️  Перезапустите терминал для применения изменений PATH" "Yellow"
}

# Основная функция
function Main {
    # Проверка прав администратора
    if ([bool]([Security.Principal.WindowsIdentity]::GetCurrent().Groups -match 'S-1-5-32-544')) {
        Write-Warning "Не рекомендуется запускать установку от администратора"
        $answer = Read-Host "Продолжить? (y/N)"
        if ($answer -notmatch '^[Yy]$') {
            exit 1
        }
    }
    
    Write-Header
    Test-Dependencies
    $targetPath = Get-InstallDirectory
    Install-Files -TargetPath $targetPath
    New-Launcher -InstallDir $targetPath
    Test-Installation -InstallDir $targetPath
    Show-CompletionInfo -InstallDir $targetPath
}

# Обработка ошибок
trap {
    Write-Host ""
    Write-Error "Установка прервана: $_"
    exit 1
}

# Запуск
Main