@echo off
REM Reset Database Script for Windows
REM This script deletes the database and seed flag to force a fresh seed on next startup

echo Resetting database...
echo.

REM Delete database file
if exist "instance\cwmt.db" (
    del "instance\cwmt.db"
    echo [32m[OK][0m Deleted instance\cwmt.db
) else (
    echo [33m[INFO][0m instance\cwmt.db not found
)

REM Delete seed flag
if exist "instance\.seeded" (
    del "instance\.seeded"
    echo [32m[OK][0m Deleted instance\.seeded
) else (
    echo [33m[INFO][0m instance\.seeded not found
)

echo.
echo [32mDatabase reset complete![0m
echo [36mRun 'python run.py' to start the app with fresh seeded data[0m
pause
