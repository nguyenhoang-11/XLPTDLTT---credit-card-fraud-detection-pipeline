@echo off
REM Quick script to run data consolidation and analysis on Windows

echo ================================================================================
echo   CREDIT CARD TRANSACTION ANALYSIS - QUICK RUN
echo ================================================================================

REM Check if docker-compose is running
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo Starting Docker services...
    docker-compose up -d
    echo Waiting for services to start 30 seconds...
    timeout /t 30 /nobreak
)

echo.
echo Step 1: Running Data Consolidation...
echo --------------------------------------------------------------------------------
docker exec -it airflow python3 -m src.data_consolidation
if errorlevel 1 (
    echo Running from consumer container instead...
    docker exec -it credit-consumer python3 -m src.data_consolidation
)

echo.
echo Step 2: Running 10 Questions Analysis...
echo --------------------------------------------------------------------------------
docker exec -it airflow python3 -m src.analyze_10_questions
if errorlevel 1 (
    echo Running from consumer container instead...
    docker exec -it credit-consumer python3 -m src.analyze_10_questions
)

echo.
echo Step 3: Copying Files to Local...
echo --------------------------------------------------------------------------------
docker cp airflow:/app/powerbi_exports ./powerbi_exports
if errorlevel 1 (
    docker cp credit-consumer:/app/powerbi_exports ./powerbi_exports
)

echo.
echo ================================================================================
echo   ANALYSIS COMPLETED!
echo ================================================================================
echo.
echo CSV files are now in: .\powerbi_exports\
echo.
echo Next steps:
echo   1. Open Power BI Web: https://app.powerbi.com
echo   2. Upload CSV files from .\powerbi_exports\
echo   3. Create visualizations
echo.
echo See detailed instructions: docs\POWERBI_SETUP.md
echo.
echo ================================================================================

pause
