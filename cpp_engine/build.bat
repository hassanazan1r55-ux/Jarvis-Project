@echo off
echo 🚀 Building C++ Audio Engine...
echo ========================================

REM Check if g++ is available
where g++ >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ g++ not found! Please install MinGW.
    pause
    exit /b 1
)

echo ✅ Compiler found: 
g++ --version | findstr "g++"

echo.
echo 📦 Compiling audio_engine.cpp...

REM Compile with proper flags
g++ -c audio_engine.cpp -o audio_engine.o -std=c++11 -Wall -O2 -mwindows -DWIN32_LEAN_AND_MEAN

if %errorlevel% neq 0 (
    echo ❌ Compilation failed!
    echo Check audio_engine.cpp for errors.
    pause
    exit /b 1
)

echo ✅ Compilation successful!

echo.
echo 📦 Creating DLL...

REM Create DLL
g++ -shared -o audio_engine.dll audio_engine.o -lwinmm -lgdi32 -std=c++11 -mwindows

if %errorlevel% neq 0 (
    echo ❌ DLL creation failed!
    pause
    exit /b 1
)

echo ✅ DLL created successfully!
echo.
echo 📁 Files created:
dir audio_engine.dll

echo.
echo ========================================
echo ✅ Build Complete! 
echo 🚀 audio_engine.dll is ready to use!
echo ========================================
pause