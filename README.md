# 💳 Credit Card Fraud Detection Pipeline - Real-time Streaming

**Đồ án XLDLTT - HD10 | GV: Phạm Minh Tú | HCMUS**

---

## 📋 Tổng Quan

Hệ thống xử lý giao dịch thẻ tín dụng **REAL-TIME** với Kafka, Spark Streaming, Hadoop HDFS, Apache Airflow, và Power BI.

### Tính năng chính:

✅ **Stream Processing**: Kafka Producer stream data với delay 0.5-2s mỗi record (mô phỏng real-time)
✅ **Fraud Detection**: Spark Consumer lọc giao dịch lỗi và gian lận
✅ **Currency Conversion**: Chuyển đổi USD → VND theo tỉ giá VietcomBank
✅ **Deduplication**: Loại bỏ duplicate records trong streaming với watermark 24h
✅ **Loop Mode**: Producer tự động loop để stream liên tục
✅ **HDFS Storage**: Lưu trữ phân tán, có thể scale
✅ **Power BI Streaming**: Tự động push data mỗi 5 phút qua REST API
✅ **Airflow Automation**: Workflow orchestration với schedule mỗi 5 phút

---

## 🏗️ Kiến Trúc Hệ Thống

```
CSV File (19,964 records)
    ↓
Kafka Producer (delay 0.5-2s, LOOP mode)
    ↓
Kafka Topic: credit_card_transactions
    ↓
Spark Streaming Consumer
  ├─ Filter: Errors & Fraud
  ├─ Transform: USD → VND
  ├─ Deduplication: Watermark 24h
  └─ Enrich: Time features
    ↓
HDFS (/user/credit-pipeline/output/transactions)
    ↓
Airflow (schedule: */5 * * * *)
  ├─ Read new data from HDFS
  ├─ Export to CSV
  ├─ Push to Power BI Streaming Dataset (REST API)
  └─ Track timestamp để tránh duplicate
    ↓
Power BI Dashboard (Auto refresh)
```

---

## 🚀 Hướng Dẫn Chạy Hệ Thống

### Bước 1: Clone Repository

```bash
git clone <repository-url>
cd XLPTDLTT---credit-card-fraud-detection-pipeline
```

### Bước 2: Tạo Power BI Streaming Dataset

1. Vào https://app.powerbi.com
2. Workspace → **+ New** → **Streaming dataset** → **API**
3. Dataset name: `credit_transactions_realtime`
4. Thêm 15 fields:

| Field Name | Type |
|-----------|------|
| transaction_datetime | DateTime |
| Amount_USD | Number |
| Amount_VND | Number |
| Merchant_Name | Text |
| Merchant_City | Text |
| Merchant_State | Text |
| MCC | Number |
| Is_Fraud | Text |
| transaction_type | Text |
| day_of_week | Number |
| transaction_year | Number |
| transaction_month | Number |
| transaction_hour | Number |
| User | Number |
| Card | Number |

5. ✅ Tích **Historic data analysis**
6. Click **Create** → **Copy Push URL**

### Bước 3: Cấu hình .env

Tạo file `.env` trong thư mục gốc:

```env
# Power BI Streaming Dataset Push URL
POWERBI_STREAMING_URL=https://api.powerbi.com/beta/.../datasets/.../rows?key=...

# Optional: Override default settings
KAFKA_BROKER=kafka:9092
```

### Bước 4: Khởi động Docker

```bash
# Build và start tất cả services
docker-compose build
docker-compose up -d

# Đợi 60-90 giây để services khởi động
```

### Bước 5: Kiểm tra Logs

```bash
# Kafka Producer (stream data)
docker logs -f credit-producer

# Spark Consumer (xử lý & lưu HDFS)
docker logs -f credit-consumer

# Airflow (push lên Power BI)
docker logs -f airflow
```

### Bước 6: Vào Airflow UI

```
URL: http://localhost:8080
Username: admin
Password: admin
```

**Kiểm tra:**
- DAG `powerbi_streaming_upload` phải **ON** (màu xanh)
- Sau 5 phút, xem **Runs** có thành công không

### Bước 7: Kiểm tra Power BI

Vào https://app.powerbi.com → Workspace → Dataset

Refresh trang (F5) → Thấy số lượng rows tăng dần mỗi 5 phút!

---

## 📊 Timeline Demo (30 phút)

| Thời gian | Producer Streamed | HDFS | Airflow Push | Power BI Rows |
|-----------|------------------|------|--------------|---------------|
| T+0 | 0 | 0 | - | 0 |
| T+5 phút | ~150-600 | ~150-600 | Lần 1 ✅ | ~150-600 |
| T+10 phút | ~300-1,200 | ~300-1,200 | Lần 2 ✅ | ~300-1,200 |
| T+15 phút | ~450-1,800 | ~450-1,800 | Lần 3 ✅ | ~450-1,800 |
| T+30 phút | ~900-3,600 | ~900-3,600 | Lần 7 ✅ | ~900-3,600 |

**Delay:** 0.5-2s mỗi record → Trong 30 phút có ~900-3,600 records

---

## 🛑 Tạm dừng & Tiếp tục

### Ngừng hệ thống (giữ data):

```bash
docker-compose stop
```

### Chạy tiếp mai:

```bash
docker-compose start
```

### Reset hoàn toàn (xóa tất cả data):

```bash
# Xóa tracking file trên host
del powerbi_exports\last_push_timestamp.txt

# Reset HDFS (cần containers đang chạy)
docker exec namenode hdfs dfs -rm -r /user/credit-pipeline/output/transactions
docker exec namenode hdfs dfs -rm -r /user/credit-pipeline/checkpoints

# Hoặc reset hoàn toàn
docker-compose down -v
docker-compose build
docker-compose up -d
```

---

## 📁 Cấu Trúc Thư Mục

```
XLPTDLTT---credit-card-fraud-detection-pipeline/
│
├── src/
│   ├── kafka_producer.py              # Producer (loop mode, 0.5-2s delay)
│   ├── spark_streaming_consumer.py    # Consumer (deduplication, watermark 24h)
│   └── exchange_rate_scraper.py       # VietcomBank rate scraper
│
├── dags/
│   └── powerbi_streaming_dag.py       # Airflow DAG (schedule: */5 * * * *)
│
├── scripts/
│   └── reset_hdfs.cmd                 # Script xóa data cũ trong HDFS
│
├── data/
│   └── User0_credit_card_transactions.csv  # 19,964 records
│
├── powerbi_exports/                   # CSV tạm & tracking file
│   ├── all_transactions.csv
│   └── last_push_timestamp.txt
│
├── docker-compose.yml                 # Docker orchestration
├── Dockerfile.airflow                 # Custom Airflow với Java
├── .env                               # Power BI Streaming URL
├── requirements.txt
├── README.md                          # File này
└── HUONG_DAN_DEMO_REALTIME.md        # Hướng dẫn demo chi tiết
```

---

## 🔧 Các Tính Năng Kỹ Thuật

### 1. Loop Mode (Producer)

Producer tự động loop khi stream hết 19,964 records:

```python
# kafka_producer.py:52-111
while True:
    loop_iteration += 1
    # Stream all records
    for row in csv_reader:
        # Loop 2+: Update timestamp to NOW
        if loop_iteration > 1:
            row["Year"] = str(now.year)
            row["Month"] = str(now.month)
            # ...
        time.sleep(random.uniform(0.5, 2))

    # Restart after 5s
    time.sleep(5)
```

### 2. Deduplication (Spark Consumer)

Loại bỏ duplicate dựa trên unique key:

```python
# spark_streaming_consumer.py:194-202
df_watermarked = df_filtered.withWatermark("transaction_datetime", "24 hours")
df_deduplicated = df_watermarked.dropDuplicates([
    "transaction_datetime", "User", "Card", "Amount_USD"
])
```

### 3. Timestamp Tracking (Airflow)

Chỉ push records mới, tránh duplicate trên Power BI:

```python
# powerbi_streaming_dag.py:58-74
tracking_file = "/app/powerbi_exports/last_push_timestamp.txt"
if os.path.exists(tracking_file):
    last_timestamp = f.read().strip()
    df = df.filter(col('transaction_datetime') > last_timestamp)

# After push:
max_timestamp = df_filtered['transaction_datetime'].max()
with open(tracking_file, 'w') as f:
    f.write(str(max_timestamp))
```

### 4. Auto-restart (Docker Compose)

Producer và Consumer tự động restart khi crash:

```yaml
# docker-compose.yml:56,68
producer:
  restart: unless-stopped

consumer:
  restart: unless-stopped
```

---

## ❓ Troubleshooting

### 1. Producer không stream

```bash
docker logs credit-producer
# Nếu báo "CSV file not found" → Kiểm tra data/User0_credit_card_transactions.csv
```

### 2. Airflow báo "No new data"

Xóa tracking file:

```bash
docker exec airflow rm -f /app/powerbi_exports/last_push_timestamp.txt
docker exec airflow airflow dags trigger powerbi_streaming_upload
```

### 3. Power BI báo 404 Not Found

URL sai hoặc dataset bị xóa:

1. Tạo lại dataset trên Power BI
2. Copy URL mới
3. Update `.env`
4. `docker-compose down && docker-compose up -d`

### 4. HDFS Connection Failed

```bash
docker exec namenode hdfs dfsadmin -report
# Nếu safe mode: hdfs dfsadmin -safemode leave
```

### 5. Power BI không auto-refresh

Dashboard cần bật auto-refresh:

1. Mở Dashboard trên Power BI Web
2. Settings → Refresh interval → Set **1 minute**
3. Hoặc bấm F5 thủ công mỗi 5 phút

---

## 📈 10 Câu Hỏi Nghiên Cứu

Dashboard Power BI trả lời các câu hỏi sau dựa trên 15 fields:

1. **Thời điểm nào trong ngày có nhiều giao dịch?** → `transaction_hour`
2. **Thành phố nào có tổng giá trị cao nhất?** → `Merchant_City`, `Amount_VND`
3. **Merchant nào có nhiều giao dịch nhất?** → `Merchant_Name`
4. **Tỷ lệ fraud theo địa điểm?** → `Is_Fraud`, `Merchant_City`
5. **User nào có nhiều giao dịch liên tiếp?** → `User`, `transaction_datetime`
6. **Giao dịch giá trị lớn ở đâu?** → `Amount_USD > 500`, `Merchant_City`
7. **Xu hướng fraud theo thời gian?** → `Is_Fraud`, `transaction_year`, `transaction_month`
8. **Khác biệt ngày thường vs cuối tuần?** → `day_of_week`, `transaction_type`
9. **User nào có nhiều fraud?** → `User`, `Is_Fraud`
10. **Đề xuất cải tiến hệ thống?** → Recommendations từ phân tích

---

## 🎯 Kết Quả Mong Đợi

### Real-time Processing:
- ✅ Kafka stream 0.5-2s/record
- ✅ Spark process real-time
- ✅ Filter fraud & errors
- ✅ Deduplication with watermark
- ✅ USD → VND conversion
- ✅ Save to HDFS

### Power BI Integration:
- ✅ Airflow schedule mỗi 5 phút
- ✅ Auto push new data via REST API
- ✅ Timestamp tracking (no duplicate)
- ✅ Dashboard auto-refresh
- ✅ 15 fields cho phân tích đầy đủ

### Demo:
- ✅ Dashboard tăng từ 0 → 900-3,600 rows trong 30 phút
- ✅ Real-time growth visualization
- ✅ Trả lời được 10 câu hỏi nghiên cứu

---

## 📚 Tài Liệu Tham Khảo

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [Hadoop HDFS](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html)
- [Apache Airflow](https://airflow.apache.org/docs/)
- [Power BI Streaming Dataset](https://learn.microsoft.com/en-us/power-bi/connect-data/service-real-time-streaming)

---

## 📝 Ghi Chú Quan Trọng

### Về Deduplication:
- Spark watermark chỉ nhớ **24 giờ**
- Nếu Producer loop sau >24h, có thể có duplicate (hiếm)
- Đối với demo, 24h là đủ

### Về Tracking File:
- File `/app/powerbi_exports/last_push_timestamp.txt` nằm trong **bind-mount volume**
- `docker-compose down -v` **KHÔNG XÓA** file này
- Phải xóa thủ công trên host nếu muốn reset

### Về Power BI Refresh:
- Power BI **KHÔNG TỰ ĐỘNG refresh** trên browser
- Cần bấm F5 hoặc bật auto-refresh 1 phút trong settings
- Backend đã nhận data ngay lập tức

---

## 🎓 Credits

**Đồ án:** CSC17106 - Xử Lý Phân Tích Dữ Liệu Trực Tuyến
**Giảng viên:** Phạm Minh Tú
**Trường:** Đại học Khoa học Tự nhiên - ĐHQG TP.HCM

---
