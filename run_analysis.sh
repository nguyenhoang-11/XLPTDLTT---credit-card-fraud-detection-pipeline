#!/bin/bash
# Quick script to run data consolidation and analysis

set -e

echo "================================================================================"
echo "  CREDIT CARD TRANSACTION ANALYSIS - QUICK RUN"
echo "================================================================================"

# Check if docker-compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Docker services not running. Starting services..."
    docker-compose up -d
    echo "⏳ Waiting for services to start (30 seconds)..."
    sleep 30
fi

echo ""
echo "Step 1: Running Data Consolidation..."
echo "--------------------------------------------------------------------------------"
docker exec -it airflow python3 -m src.data_consolidation || {
    echo "⚠️  Running from consumer container instead..."
    docker exec -it credit-consumer python3 -m src.data_consolidation
}

echo ""
echo "Step 2: Running 10 Questions Analysis..."
echo "--------------------------------------------------------------------------------"
docker exec -it airflow python3 -m src.analyze_10_questions || {
    echo "⚠️  Running from consumer container instead..."
    docker exec -it credit-consumer python3 -m src.analyze_10_questions
}

echo ""
echo "Step 3: Listing Generated Files..."
echo "--------------------------------------------------------------------------------"
echo "Main exports:"
docker exec -it airflow ls -lh /app/powerbi_exports/ 2>/dev/null || \
docker exec -it credit-consumer ls -lh /app/powerbi_exports/

echo ""
echo "Analysis exports:"
docker exec -it airflow ls -lh /app/powerbi_exports/analysis/ 2>/dev/null || \
docker exec -it credit-consumer ls -lh /app/powerbi_exports/analysis/

echo ""
echo "================================================================================"
echo "  ✅ ANALYSIS COMPLETED!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Copy CSV files to your local machine:"
echo "     docker cp airflow:/app/powerbi_exports ./powerbi_exports"
echo ""
echo "  2. Upload to Power BI Web:"
echo "     - Login to https://app.powerbi.com"
echo "     - Upload CSV files from ./powerbi_exports"
echo "     - Create visualizations"
echo ""
echo "  3. See detailed instructions:"
echo "     docs/POWERBI_SETUP.md"
echo ""
echo "================================================================================"
