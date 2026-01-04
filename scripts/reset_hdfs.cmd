@echo off
REM Reset HDFS data for fresh demo

echo ============================================
echo RESET HDFS - Clean all old transaction data
echo ============================================

echo.
echo [1/3] Deleting old transactions...
docker exec namenode hdfs dfs -rm -r /user/credit-pipeline/output/transactions

echo.
echo [2/3] Deleting Spark checkpoints...
docker exec namenode hdfs dfs -rm -r /user/credit-pipeline/checkpoints

echo.
echo [3/3] Verifying cleanup...
docker exec namenode hdfs dfs -ls /user/credit-pipeline/output/

echo.
echo ============================================
echo DONE! HDFS is now clean for fresh demo
echo ============================================
echo.
echo Next steps:
echo 1. Restart Docker: docker-compose down ^&^& docker-compose up -d
echo 2. Producer and Consumer will auto-start
echo 3. Wait 5 minutes for first Power BI update
echo ============================================
