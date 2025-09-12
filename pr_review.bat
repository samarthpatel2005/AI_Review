@echo off
REM GitHub Pull Request Review Script
REM Usage: pr_review.bat <pr_url> [output_directory]

echo.
echo ========================================
echo   GitHub Pull Request Reviewer
echo ========================================
echo.

if "%1"=="" (
    echo Usage: %0 ^<github_pr_url^> [output_directory]
    echo.
    echo Examples:
    echo   %0 https://github.com/owner/repo/pull/123
    echo   %0 https://github.com/owner/repo/pull/456 reviews\
    echo.
    echo This tool will:
    echo   - Download PR diff from GitHub
    echo   - Analyze only the changed C/C++ code
    echo   - Generate detailed review report
    echo   - Focus on security, logic, and quality issues
    echo.
    pause
    exit /b 1
)

set PYTHON_CMD="C:/Users/HP/AppData/Local/Programs/Python/Python313/python.exe"

if "%2"=="" (
    %PYTHON_CMD% pr_reviewer.py "%1"
) else (
    %PYTHON_CMD% pr_reviewer.py "%1" -o "%2"
)

pause
