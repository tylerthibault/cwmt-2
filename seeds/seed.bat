@echo off
REM Seed runner convenience script for CWMT Flask Application (Windows)
REM This script activates the virtual environment and runs the seed runner

SET SCRIPT_DIR=%~dp0
SET PROJECT_ROOT=%SCRIPT_DIR%..

REM Activate virtual environment if it exists
IF EXIST "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
) ELSE IF EXIST "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
)

REM Run the seed script with all arguments passed through
python "%SCRIPT_DIR%run_seeds.py" %*
