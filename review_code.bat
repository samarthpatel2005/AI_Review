@echo off
REM Automated C Code Review Script
REM Usage: review_code.bat <file_or_directory> [output_directory]

echo.
echo ========================================
echo   AWS Bedrock C Code Review System
echo ========================================
echo.

if "%1"=="" (
    echo Usage: %0 ^<file_or_directory^> [output_directory]
    echo.
    echo Examples:
    echo   %0 myfile.c
    echo   %0 myfile.c reviews\
    echo   %0 src\ reviews\
    echo   %0 . reviews\ -r    ^(recursive^)
    echo.
    pause
    exit /b 1
)

set PYTHON_CMD="C:/Users/HP/AppData/Local/Programs/Python/Python313/python.exe"

if "%2"=="" (
    %PYTHON_CMD% code_reviewer.py "%1"
) else (
    %PYTHON_CMD% code_reviewer.py "%1" -o "%2"
)

pause
