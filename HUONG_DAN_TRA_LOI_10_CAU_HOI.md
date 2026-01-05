# 📊 Hướng Dẫn Trả Lời 10 Câu Hỏi Phân Tích - Power BI Dashboard

**Đồ án:** CSC17106 - Xử Lý Phân Tích Dữ Liệu Trực Tuyến
**GV:** Phạm Minh Tú | HCMUS

---

## 📌 Danh sách 15 Fields có sẵn trong Power BI Dataset

| Field Name | Type | Mô tả |
|-----------|------|-------|
| `transaction_datetime` | DateTime | Thời điểm giao dịch (dd/MM/yyyy HH:mm:ss) |
| `Amount_USD` | Number | Giá trị giao dịch (USD) |
| `Amount_VND` | Number | Giá trị giao dịch (VND) |
| `Merchant_Name` | Text | Tên merchant |
| `Merchant_City` | Text | Thành phố merchant |
| `Merchant_State` | Text | Bang merchant |
| `MCC` | Number | Merchant Category Code |
| `Is_Fraud` | Text | "Yes" hoặc "No" |
| `transaction_type` | Text | FRAUD / HIGH_VALUE / MEDIUM_VALUE / LOW_VALUE |
| `day_of_week` | Number | Thứ trong tuần (1=CN, 2=T2, ..., 7=T7) |
| `transaction_year` | Number | Năm |
| `transaction_month` | Number | Tháng |
| `transaction_hour` | Number | Giờ (0-23) |
| `User` | Number | User ID |
| `Card` | Number | Card ID |

---

## ❓ Câu 1: Thời điểm nào trong ngày có nhiều giao dịch nhất? Có khung giờ nào giao dịch bất thường không?

### 🎯 Mục tiêu:
- Tìm khung giờ có **nhiều giao dịch nhất** trong ngày
- Phát hiện **khung giờ bất thường** (có giao dịch quá ít hoặc quá nhiều)

### 📊 Visuals cần tạo trong Power BI:

#### Visual 1: Column Chart - Giao dịch theo giờ
**Visualization:** Clustered Column Chart
**Axis (X):** `transaction_hour`
**Values (Y):** `Count of transaction_datetime`
**Title:** "Số lượng giao dịch theo giờ trong ngày"

**Cách đọc:**
- Trục X: Giờ (0-23)
- Trục Y: Số lượng giao dịch
- Cột cao nhất = Giờ có nhiều giao dịch nhất

#### Visual 2: Line Chart - Xu hướng theo giờ
**Visualization:** Line Chart
**Axis (X):** `transaction_hour`
**Values (Y):** `Count of transaction_datetime`
**Title:** "Xu hướng giao dịch theo giờ"

**Cách phân tích:**
- **Giờ cao điểm:** Nhìn vào cột/điểm cao nhất (VD: 10h-14h, 18h-20h)
- **Giờ bất thường:**
  - Giờ có giao dịch quá thấp (VD: 2h-5h sáng → nghi ngờ fraud)
  - Giờ có giao dịch đột biến (VD: tăng đột ngột 300% so với giờ liền kề)

### ✅ Câu trả lời mẫu:

> **Kết quả phân tích:**
> - **Giờ có nhiều giao dịch nhất:** 12h-14h (giờ ăn trưa) với ~450 giao dịch/giờ
> - **Giờ thấp điểm:** 2h-5h sáng (~20-30 giao dịch/giờ)
> - **Khung giờ bất thường:**
>   - 3h sáng có 85 giao dịch (cao gấp 3 lần so với trung bình 2h-5h) → Cần kiểm tra fraud
>   - 23h có 120 giao dịch → Có thể do mua sắm online vào đêm khuya
>
> **Biểu đồ:** [Chèn screenshot Column Chart từ Power BI]

---

## ❓ Câu 2: Thành phố nào có tổng giá trị giao dịch cao nhất? Có liên hệ với dân số hoặc vị trí không?

### 🎯 Mục tiêu:
- Top thành phố có **tổng Amount_VND cao nhất**
- Phân tích mối liên hệ với **dân số / vị trí địa lý**

### 📊 Visuals cần tạo:

#### Visual 1: Bar Chart - Top 10 thành phố
**Visualization:** Clustered Bar Chart (ngang)
**Axis (Y):** `Merchant_City`
**Values (X):** `Sum of Amount_VND`
**Filters:** Top 10 by Sum of Amount_VND
**Title:** "Top 10 thành phố có tổng giá trị giao dịch cao nhất"

#### Visual 2: Table - Chi tiết thành phố
**Visualization:** Table
**Columns:**
- `Merchant_City`
- `Count of transaction_datetime` (Số giao dịch)
- `Sum of Amount_VND` (Tổng giá trị)
- `Average of Amount_VND` (Giá trị trung bình)

**Sort:** By `Sum of Amount_VND` descending

#### Visual 3: Map - Phân bố địa lý
**Visualization:** Map
**Location:** `Merchant_City`, `Merchant_State`
**Size:** `Sum of Amount_VND`
**Title:** "Phân bố giao dịch theo địa lý"

### ✅ Câu trả lời mẫu:

> **Top 5 thành phố có tổng giá trị cao nhất:**
> 1. **New York, NY:** 1,250,000,000 VND (~52,000 USD) - 450 giao dịch
> 2. **Los Angeles, CA:** 980,000,000 VND (~41,000 USD) - 380 giao dịch
> 3. **Chicago, IL:** 720,000,000 VND (~30,000 USD) - 290 giao dịch
> 4. **Houston, TX:** 650,000,000 VND (~27,000 USD) - 270 giao dịch
> 5. **Phoenix, AZ:** 580,000,000 VND (~24,000 USD) - 240 giao dịch
>
> **Phân tích liên hệ với dân số:**
> - ✅ **Có tương quan chặt chẽ:** Các thành phố lớn (NY, LA, Chicago) có dân số cao → Tổng giá trị giao dịch cao
> - ✅ **Vị trí địa lý:** Các thành phố ven biển (NY, LA) có giá trị giao dịch cao hơn các thành phố nội địa
> - ⚠️ **Bất thường:** Phoenix (dân số thấp hơn Philadelphia) nhưng có tổng giá trị cao hơn → Có thể do nhiều resort/du lịch
>
> **Biểu đồ:** [Chèn screenshot Bar Chart + Map]

---

## ❓ Câu 3: Merchant nào có số lượng hoặc giá trị giao dịch cao nhất?

### 🎯 Mục tiêu:
- Top merchant theo **số lượng giao dịch**
- Top merchant theo **tổng giá trị giao dịch**

### 📊 Visuals cần tạo:

#### Visual 1: Bar Chart - Top 10 Merchant theo số lượng
**Visualization:** Clustered Bar Chart
**Axis (Y):** `Merchant_Name`
**Values (X):** `Count of transaction_datetime`
**Filters:** Top 10 by Count
**Title:** "Top 10 Merchant theo số lượng giao dịch"

#### Visual 2: Bar Chart - Top 10 Merchant theo giá trị
**Visualization:** Clustered Bar Chart
**Axis (Y):** `Merchant_Name`
**Values (X):** `Sum of Amount_VND`
**Filters:** Top 10 by Sum of Amount_VND
**Title:** "Top 10 Merchant theo tổng giá trị giao dịch"

#### Visual 3: Scatter Chart - Số lượng vs Giá trị
**Visualization:** Scatter Chart
**X Axis:** `Count of transaction_datetime`
**Y Axis:** `Sum of Amount_VND`
**Details:** `Merchant_Name`
**Title:** "Mối quan hệ giữa số lượng và giá trị giao dịch"

### ✅ Câu trả lời mẫu:

> **Top 5 Merchant theo SỐ LƯỢNG giao dịch:**
> 1. **Walmart:** 350 giao dịch
> 2. **Target:** 280 giao dịch
> 3. **Starbucks:** 260 giao dịch
> 4. **McDonald's:** 245 giao dịch
> 5. **Amazon:** 220 giao dịch
>
> **Top 5 Merchant theo TỔNG GIÁ TRỊ:**
> 1. **Apple Store:** 450,000,000 VND (120 giao dịch, giá trị TB: 3,750,000 VND)
> 2. **Tesla:** 380,000,000 VND (25 giao dịch, giá trị TB: 15,200,000 VND)
> 3. **Best Buy:** 320,000,000 VND (180 giao dịch, giá trị TB: 1,778,000 VND)
> 4. **Whole Foods:** 280,000,000 VND (240 giao dịch, giá trị TB: 1,167,000 VND)
> 5. **Costco:** 250,000,000 VND (200 giao dịch, giá trị TB: 1,250,000 VND)
>
> **Nhận xét:**
> - Merchant có **SỐ LƯỢNG cao** (Walmart, Starbucks) thường là hàng tiêu dùng giá rẻ
> - Merchant có **GIÁ TRỊ cao** (Tesla, Apple) có ít giao dịch nhưng giá trị trung bình rất lớn
> - **Scatter Chart** cho thấy 2 nhóm rõ ràng: High-volume/Low-value vs Low-volume/High-value

---

## ❓ Câu 4: Thành phố hoặc merchant nào có tỷ lệ fraud cao bất thường?

### 🎯 Mục tiêu:
- Tính **tỷ lệ fraud (%)** theo thành phố và merchant
- Phát hiện outlier có tỷ lệ fraud cao bất thường

### 📊 Visuals cần tạo:

#### Visual 1: Table - Tỷ lệ fraud theo thành phố
**Visualization:** Table
**Columns:**
- `Merchant_City`
- `Total Transactions` = `COUNT(transaction_datetime)`
- `Fraud Transactions` = `CALCULATE(COUNT(transaction_datetime), Is_Fraud = "Yes")`
- `Fraud Rate (%)` = `([Fraud Transactions] / [Total Transactions]) * 100`

**Sort:** By Fraud Rate (%) descending
**Filter:** Chỉ hiện thành phố có ≥ 20 giao dịch (để tránh nhiễu)

#### Visual 2: Bar Chart - Top 10 thành phố có fraud rate cao
**Visualization:** Clustered Bar Chart
**Axis (Y):** `Merchant_City`
**Values (X):** `Fraud Rate (%)`
**Filters:** Top 10, Total Transactions ≥ 20
**Title:** "Top 10 thành phố có tỷ lệ fraud cao nhất"

#### Visual 3: Table - Tỷ lệ fraud theo merchant
**Visualization:** Table
**Columns:** (Tương tự như Visual 1 nhưng dùng `Merchant_Name`)

### 💡 Cách tạo Calculated Measures trong Power BI:

```DAX
// Measure 1: Total Transactions
Total Transactions = COUNT(RealTimeData[transaction_datetime])

// Measure 2: Fraud Transactions
Fraud Transactions = CALCULATE(
    COUNT(RealTimeData[transaction_datetime]),
    RealTimeData[Is_Fraud] = "Yes"
)

// Measure 3: Fraud Rate
Fraud Rate (%) =
DIVIDE(
    [Fraud Transactions],
    [Total Transactions],
    0
) * 100
```

### ✅ Câu trả lời mẫu:

> **Thành phố có tỷ lệ fraud cao bất thường:**
>
> | Thành phố | Tổng GD | Fraud | Tỷ lệ (%) | Nhận xét |
> |-----------|---------|-------|-----------|----------|
> | **Miami, FL** | 45 | 12 | **26.7%** | ⚠️ Cao gấp 5 lần TB (5.2%) |
> | **Las Vegas, NV** | 38 | 9 | **23.7%** | ⚠️ Thành phố du lịch, nhiều giao dịch lạ |
> | **Newark, NJ** | 52 | 11 | **21.2%** | ⚠️ Gần New York, có thể ảnh hưởng từ fraud ring |
> | **Detroit, MI** | 67 | 8 | **11.9%** | ⚠️ Cao hơn TB nhưng chấp nhận được |
> | **New York, NY** | 450 | 18 | **4.0%** | ✅ Thấp hơn TB (nhiều GD hợp lệ) |
>
> **Merchant có tỷ lệ fraud cao:**
>
> | Merchant | Tổng GD | Fraud | Tỷ lệ (%) | Nhận xét |
> |----------|---------|-------|-----------|----------|
> | **Gas Station XYZ** | 28 | 11 | **39.3%** | 🚨 Cực kỳ cao! Cần kiểm tra ngay |
> | **Online Electronics** | 42 | 14 | **33.3%** | 🚨 Merchant online dễ bị tấn công |
> | **Jewelry Store ABC** | 35 | 9 | **25.7%** | ⚠️ Hàng giá trị cao → mục tiêu fraud |
>
> **Khuyến nghị:**
> - Block/Review tất cả giao dịch từ Gas Station XYZ và Online Electronics
> - Tăng cường xác thực 2FA cho các thành phố Miami, Las Vegas

---

## ❓ Câu 5: Người dùng nào có nhiều giao dịch liên tiếp trong thời gian ngắn?

### 🎯 Mục tiêu:
- Tìm user có **tần suất giao dịch cao bất thường** (VD: >10 giao dịch trong 1 giờ)
- Phát hiện hành vi **velocity attack** (tấn công liên tiếp)

### 📊 Visuals cần tạo:

#### Visual 1: Table - Top users có nhiều giao dịch
**Visualization:** Table
**Columns:**
- `User`
- `Count of transaction_datetime` (Tổng giao dịch)
- `Earliest Transaction` = `MIN(transaction_datetime)`
- `Latest Transaction` = `MAX(transaction_datetime)`
- `Time Span (hours)` = Tính khoảng thời gian

**Sort:** By Count descending
**Filter:** Top 20

#### Visual 2: Scatter Chart - Giao dịch theo thời gian
**Visualization:** Scatter Chart
**X Axis:** `transaction_datetime`
**Y Axis:** `User`
**Size:** `Amount_VND`
**Legend:** `Is_Fraud`
**Title:** "Timeline giao dịch của từng User"

**Cách đọc:**
- Nếu thấy nhiều điểm tập trung dày đặc trong 1 khoảng thời gian ngắn → User đáng nghi

### 💡 Calculated Column để tính Time Span:

```DAX
// Tạo Calculated Table trong Power BI
User Activity Summary =
SUMMARIZE(
    RealTimeData,
    RealTimeData[User],
    "Total Transactions", COUNT(RealTimeData[transaction_datetime]),
    "First Transaction", MIN(RealTimeData[transaction_datetime]),
    "Last Transaction", MAX(RealTimeData[transaction_datetime]),
    "Time Span (Hours)",
        DATEDIFF(
            MIN(RealTimeData[transaction_datetime]),
            MAX(RealTimeData[transaction_datetime]),
            HOUR
        )
)

// Thêm Calculated Column: Transaction Velocity
Transaction Velocity =
DIVIDE(
    [Total Transactions],
    [Time Span (Hours)] + 1,  // +1 để tránh chia cho 0
    0
)
```

### ✅ Câu trả lời mẫu:

> **Top 5 User có nhiều giao dịch liên tiếp:**
>
> | User ID | Tổng GD | Thời gian | Time Span | Velocity (GD/giờ) | Nhận xét |
> |---------|---------|-----------|-----------|-------------------|----------|
> | **User 1234** | 45 | 10:00-12:30 | 2.5h | **18 GD/giờ** | 🚨 Bất thường! TB: 2-3 GD/giờ |
> | **User 5678** | 38 | 14:15-16:00 | 1.75h | **21.7 GD/giờ** | 🚨 Có thể bị đánh cắp thẻ |
> | **User 9012** | 32 | 09:00-11:00 | 2h | **16 GD/giờ** | ⚠️ Cần kiểm tra |
> | **User 3456** | 28 | 18:00-19:00 | 1h | **28 GD/giờ** | 🚨 Cực kỳ cao! |
> | **User 7890** | 150 | 08:00-20:00 | 12h | 12.5 GD/giờ | ✅ Bình thường (cả ngày) |
>
> **Phát hiện velocity attack:**
> - **User 3456:** 28 giao dịch trong 1 giờ (18:00-19:00)
>   - 15/28 giao dịch bị fraud (53.6%)
>   - Các giao dịch cách nhau ~2 phút → Nghi ngờ bot tự động
> - **User 5678:** 38 giao dịch trong 1.75 giờ
>   - Tất cả ở cùng merchant "Online Electronics"
>   - Giá trị trung bình: $150 → Có thể test card stolen
>
> **Biểu đồ:** [Scatter Chart hiển thị các điểm giao dịch tập trung dày đặc]

---

## ❓ Câu 6: Giao dịch có giá trị lớn thường xảy ra vào thời điểm nào? Ở đâu?

### 🎯 Mục tiêu:
- Tìm **khung giờ** có nhiều giao dịch giá trị lớn (Amount_USD > $500)
- Tìm **thành phố/merchant** có giao dịch giá trị lớn

### 📊 Visuals cần tạo:

#### Visual 1: Column Chart - Giao dịch giá trị lớn theo giờ
**Visualization:** Clustered Column Chart
**Axis (X):** `transaction_hour`
**Values (Y):** `Count of transaction_datetime`
**Filters:** `transaction_type = "HIGH_VALUE"` (Amount_USD > $500)
**Title:** "Phân bố giao dịch giá trị lớn theo giờ"

#### Visual 2: Stacked Bar Chart - Giao dịch lớn theo thành phố
**Visualization:** Stacked Bar Chart
**Axis (Y):** `Merchant_City`
**Values (X):** `Count of transaction_datetime`
**Legend:** `transaction_type`
**Filters:** Top 10 cities
**Title:** "Giao dịch giá trị lớn theo thành phố"

#### Visual 3: Table - Chi tiết giao dịch lớn
**Visualization:** Table
**Columns:**
- `Merchant_City`
- `Merchant_Name`
- `Count (HIGH_VALUE)`
- `Sum of Amount_VND` (chỉ HIGH_VALUE)
- `Average of Amount_VND`

**Filters:** `transaction_type = "HIGH_VALUE"`

### ✅ Câu trả lời mẫu:

> **Thời điểm có nhiều giao dịch giá trị lớn:**
> - **10:00-12:00:** 45 giao dịch > $500 (cao nhất)
>   - Giờ mở cửa Apple Store, Tesla showroom
> - **14:00-16:00:** 38 giao dịch > $500
>   - Giờ cao điểm mua sắm trực tuyến
> - **19:00-21:00:** 32 giao dịch > $500
>   - Mua sắm sau giờ làm việc
> - **02:00-05:00:** 12 giao dịch > $500
>   - ⚠️ Bất thường! Cần kiểm tra fraud (8/12 giao dịch là fraud)
>
> **Địa điểm có giao dịch giá trị lớn:**
>
> | Thành phố | Số GD >$500 | Tổng giá trị | Merchant phổ biến |
> |-----------|-------------|--------------|-------------------|
> | **New York, NY** | 85 | $65,000 | Apple Store, Tiffany & Co |
> | **Los Angeles, CA** | 72 | $58,000 | Tesla, Beverly Hills Boutique |
> | **San Francisco, CA** | 68 | $54,000 | Apple Store, Nordstrom |
> | **Miami, FL** | 45 | $42,000 | Luxury Hotels, Yacht Rentals |
>
> **Merchant có nhiều giao dịch giá trị lớn:**
> 1. **Tesla:** 28 giao dịch, giá trị TB: $15,200
> 2. **Apple Store:** 45 giao dịch, giá trị TB: $3,750
> 3. **Louis Vuitton:** 18 giao dịch, giá trị TB: $2,800
>
> **Nhận xét:**
> - Giao dịch lớn tập trung vào **giờ hành chính** (10h-16h)
> - Các thành phố lớn và giàu có (NY, LA, SF) có nhiều giao dịch lớn
> - ⚠️ Giao dịch lớn vào **đêm khuya** (2h-5h) có tỷ lệ fraud rất cao (66.7%)

---

## ❓ Câu 7: Có xu hướng nào trong các giao dịch bị fraud không? (giờ, merchant, city,...)

### 🎯 Mục tiêu:
- Phát hiện **pattern** của giao dịch fraud theo nhiều chiều

### 📊 Visuals cần tạo:

#### Visual 1: Heatmap - Fraud theo giờ và ngày trong tuần
**Visualization:** Matrix
**Rows:** `day_of_week` (1=CN, 2=T2, ..., 7=T7)
**Columns:** `transaction_hour`
**Values:** `Fraud Rate (%)`
**Conditional Formatting:** Color scale (đỏ = cao, xanh = thấp)
**Title:** "Heatmap: Tỷ lệ fraud theo giờ và thứ"

#### Visual 2: Column Chart - Fraud theo giờ
**Visualization:** Clustered Column Chart
**Axis (X):** `transaction_hour`
**Values (Y):**
- `Total Transactions`
- `Fraud Transactions`
**Title:** "So sánh giao dịch tổng và fraud theo giờ"

#### Visual 3: Pie Chart - Fraud theo loại merchant (MCC)
**Visualization:** Pie Chart
**Legend:** `MCC`
**Values:** `Count of transaction_datetime`
**Filters:** `Is_Fraud = "Yes"`
**Title:** "Phân bố fraud theo loại merchant (MCC)"

#### Visual 4: Bar Chart - Top merchant có fraud
**Visualization:** Clustered Bar Chart
**Axis (Y):** `Merchant_Name`
**Values (X):** `Count of fraud transactions`
**Filters:** Top 10
**Title:** "Top 10 merchant bị fraud nhiều nhất"

### ✅ Câu trả lời mẫu:

> **Xu hướng fraud theo THỜI GIAN:**
>
> **Theo giờ trong ngày:**
> - **Cao nhất:** 2h-5h sáng (tỷ lệ fraud: 15-25%)
>   - Giờ ít giao dịch hợp lệ, fraudster tận dụng
> - **Thấp nhất:** 10h-14h (tỷ lệ fraud: 2-4%)
>   - Giờ cao điểm, nhiều giao dịch hợp lệ
> - **Spike bất thường:** 23h (tỷ lệ fraud: 12%)
>   - Có thể do online shopping đêm khuya
>
> **Theo thứ trong tuần:**
> - **Cuối tuần (CN, T7):** Tỷ lệ fraud cao hơn 30% so với ngày thường
>   - Lý do: Ngân hàng/support ít hoạt động, fraudster tận dụng
> - **Thứ 2:** Tỷ lệ fraud thấp nhất (3.8%)
>   - Mọi người quay lại làm việc, giao dịch hợp lệ tăng
>
> **Heatmap insights:**
> - 🔴 **Hot spot:** Chủ nhật 2h-4h sáng (fraud rate: 28%)
> - 🔴 **Hot spot:** Thứ 7 23h-01h (fraud rate: 22%)
> - 🟢 **Safe zone:** Thứ 2-5, 10h-14h (fraud rate: <3%)
>
> ---
>
> **Xu hướng fraud theo ĐỊA ĐIỂM:**
>
> **Top 5 thành phố bị fraud nhiều:**
> 1. **Miami, FL:** 26.7% fraud rate (12/45 giao dịch)
> 2. **Las Vegas, NV:** 23.7% (9/38)
> 3. **Newark, NJ:** 21.2% (11/52)
> 4. **Atlantic City, NJ:** 18.5% (7/38)
> 5. **Detroit, MI:** 11.9% (8/67)
>
> **Nhận xét:**
> - Thành phố du lịch (Miami, Las Vegas) có fraud cao
> - Thành phố gần cảng/sân bay (Newark) dễ bị tấn công
>
> ---
>
> **Xu hướng fraud theo MERCHANT:**
>
> **Top 5 loại merchant (MCC) bị fraud:**
> 1. **MCC 5541 (Gas Stations):** 35% fraud rate
> 2. **MCC 5732 (Electronics Stores):** 28% fraud rate
> 3. **MCC 5944 (Jewelry):** 24% fraud rate
> 4. **MCC 5812 (Restaurants):** 8% fraud rate
> 5. **MCC 5411 (Grocery):** 4% fraud rate
>
> **Merchant cụ thể:**
> - **Gas Station XYZ:** 11/28 giao dịch là fraud (39.3%)
> - **Online Electronics:** 14/42 giao dịch là fraud (33.3%)
> - **Jewelry Store ABC:** 9/35 giao dịch là fraud (25.7%)
>
> ---
>
> **TỔNG HỢP XU HƯỚNG:**
> 1. ⏰ **Thời gian:** Đêm khuya (2h-5h) + Cuối tuần
> 2. 📍 **Địa điểm:** Thành phố du lịch (Miami, Vegas)
> 3. 🏪 **Merchant:** Gas stations, Electronics, Jewelry
> 4. 💰 **Giá trị:** Giao dịch $150-$500 (không quá lớn để tránh cảnh báo)
> 5. 👤 **User:** User có velocity cao (>10 giao dịch/giờ)
>
> **Biểu đồ:** [Chèn Heatmap + Column Chart + Pie Chart]

---

## ❓ Câu 8: Có sự khác biệt nào giữa giao dịch ngày thường và cuối tuần?

### 🎯 Mục tiêu:
- So sánh **số lượng, giá trị, fraud rate** giữa weekday vs weekend

### 📊 Visuals cần tạo:

#### Visual 1: Clustered Column Chart - So sánh weekday vs weekend
**Visualization:** Clustered Column Chart
**Axis (X):** `Day Type` (tạo calculated column: Weekday/Weekend)
**Values (Y):**
- `Count of transactions`
- `Sum of Amount_VND`
- `Fraud Rate (%)`
**Title:** "So sánh giao dịch: Ngày thường vs Cuối tuần"

#### Visual 2: Line Chart - Xu hướng theo ngày trong tuần
**Visualization:** Line Chart
**Axis (X):** `day_of_week`
**Values (Y):**
- `Count of transactions`
- `Average Amount_VND`
- `Fraud Rate (%)`
**Title:** "Xu hướng giao dịch theo từng ngày trong tuần"

### 💡 Calculated Column: Day Type

```DAX
Day Type =
IF(
    RealTimeData[day_of_week] = 1 || RealTimeData[day_of_week] = 7,
    "Weekend",
    "Weekday"
)
```

### ✅ Câu trả lời mẫu:

> **So sánh Ngày thường (T2-T6) vs Cuối tuần (T7-CN):**
>
> | Chỉ số | Ngày thường | Cuối tuần | Chênh lệch |
> |--------|-------------|-----------|------------|
> | **Tổng giao dịch** | 6,850 | 1,350 | -80% |
> | **Tổng giá trị (VND)** | 4.2 tỷ | 980 triệu | -77% |
> | **Giá trị TB/GD** | 613,000 | 726,000 | **+18%** ⬆️ |
> | **Fraud rate (%)** | 4.2% | **6.8%** | **+62%** 🚨 |
> | **HIGH_VALUE (>$500)** | 8.5% | **12.3%** | **+45%** ⬆️ |
>
> **Phân tích chi tiết:**
>
> **1. Số lượng giao dịch:**
> - Ngày thường có gấp **5 lần** số giao dịch cuối tuần
> - Lý do: Mọi người đi làm, mua sắm, ăn uống nhiều hơn
>
> **2. Giá trị giao dịch:**
> - Cuối tuần có giá trị **trung bình cao hơn** 18%
> - Lý do: Mua sắm lớn, du lịch, ăn nhà hàng đắt tiền
>
> **3. Tỷ lệ fraud:**
> - Cuối tuần có fraud rate **cao gấp 1.6 lần** (6.8% vs 4.2%)
> - Lý do:
>   - Ngân hàng/support làm việc ít → Fraudster tận dụng
>   - Khách hàng ít check balance vào cuối tuần
>   - Nhiều giao dịch online/du lịch → Dễ bị tấn công
>
> **4. Loại merchant:**
> - **Ngày thường:** Grocery (25%), Gas stations (18%), Restaurants (15%)
> - **Cuối tuần:** Restaurants (28%), Entertainment (22%), Hotels (12%)
>
> **5. Khung giờ:**
> - **Ngày thường:** Peak 12h-14h (giờ ăn trưa)
> - **Cuối tuần:** Phân bố đều hơn, peak 18h-21h (giờ ăn tối)
>
> **Biểu đồ:** [Clustered Column Chart + Line Chart theo ngày trong tuần]

---

## ❓ Câu 9: Có người dùng nào bị nhiều lỗi hoặc bị gắn cờ fraud nhiều hơn mức trung bình?

### 🎯 Mục tiêu:
- Tìm **users bị fraud nhiều lần** (victim hoặc fraudster)
- Phân tích hành vi của các users này

### 📊 Visuals cần tạo:

#### Visual 1: Table - Top users bị fraud
**Visualization:** Table
**Columns:**
- `User`
- `Total Transactions`
- `Fraud Transactions`
- `Fraud Rate (%)`
- `Total Amount Lost (VND)`

**Sort:** By Fraud Transactions descending
**Filter:** Fraud Transactions > 0

#### Visual 2: Scatter Chart - Fraud rate vs Total transactions
**Visualization:** Scatter Chart
**X Axis:** `Total Transactions`
**Y Axis:** `Fraud Rate (%)`
**Details:** `User`
**Size:** `Total Amount Lost`
**Title:** "Phân tích users bị fraud"

**Cách đọc:**
- **Góc phải trên (nhiều GD, fraud rate cao):** Users bị tấn công liên tục hoặc là fraudster
- **Góc trái trên (ít GD, fraud rate cao):** Users mới bị tấn công ngay

#### Visual 3: Line Chart - Timeline fraud của top users
**Visualization:** Line Chart
**Axis (X):** `transaction_datetime`
**Values (Y):** `Cumulative Fraud Count`
**Legend:** `User` (chọn top 5 users)
**Title:** "Timeline giao dịch fraud của top users"

### 💡 Calculated Measures:

```DAX
// Measure: Fraud Transactions per User
Fraud Transactions =
CALCULATE(
    COUNT(RealTimeData[transaction_datetime]),
    RealTimeData[Is_Fraud] = "Yes"
)

// Measure: Total Amount Lost (VND)
Total Amount Lost =
CALCULATE(
    SUM(RealTimeData[Amount_VND]),
    RealTimeData[Is_Fraud] = "Yes"
)

// Measure: Average Fraud Rate
Average Fraud Rate =
AVERAGEX(
    VALUES(RealTimeData[User]),
    DIVIDE(
        CALCULATE(COUNT(RealTimeData[transaction_datetime]), RealTimeData[Is_Fraud] = "Yes"),
        CALCULATE(COUNT(RealTimeData[transaction_datetime])),
        0
    )
) * 100
```

### ✅ Câu trả lời mẫu:

> **Mức trung bình toàn hệ thống:**
> - **Fraud rate TB:** 5.2%
> - **Số fraud TB/user:** 2.3 giao dịch
> - **Amount lost TB/user:** 1,850,000 VND
>
> ---
>
> **Top 10 Users bị fraud NHIỀU NHẤT:**
>
> | User ID | Tổng GD | Fraud GD | Fraud Rate | Tổng mất (VND) | Phân tích |
> |---------|---------|----------|------------|----------------|-----------|
> | **User 1234** | 45 | **18** | 40% | 15.2M | 🚨 Thẻ bị đánh cắp! |
> | **User 5678** | 38 | **15** | 39.5% | 12.8M | 🚨 Victim hoặc fraudster |
> | **User 9012** | 52 | **14** | 26.9% | 18.5M | ⚠️ Cần khóa card ngay |
> | **User 3456** | 28 | **12** | 42.9% | 9.2M | 🚨 Cao nhất! |
> | **User 7890** | 67 | **11** | 16.4% | 22.1M | ⚠️ Nhiều GD lớn bị fraud |
> | **User 2345** | 32 | **10** | 31.3% | 8.5M | 🚨 |
> | **User 6789** | 41 | **9** | 22% | 11.3M | ⚠️ |
> | **User 0123** | 25 | **8** | 32% | 6.8M | 🚨 |
> | **User 4567** | 58 | **8** | 13.8% | 14.2M | ✅ Acceptable |
> | **User 8901** | 33 | **7** | 21.2% | 7.9M | ⚠️ |
>
> ---
>
> **Phân tích chi tiết:**
>
> **User 1234 (40% fraud rate):**
> - 45 giao dịch, 18 bị fraud
> - **Pattern:**
>   - 15/18 fraud xảy ra trong 2 ngày (04/01 - 05/01)
>   - Tất cả ở thành phố KHÁC với lịch sử (Miami vs thường ở New York)
>   - Giá trị: $150-$250 (dưới ngưỡng cảnh báo $500)
>   - Merchant: Gas stations, Electronics
> - **Kết luận:** Thẻ bị đánh cắp, fraudster test card với giao dịch nhỏ
>
> **User 3456 (42.9% fraud rate - CAO NHẤT):**
> - 28 giao dịch, 12 bị fraud
> - **Pattern:**
>   - 12 fraud xảy ra trong **1 giờ** (18:00-19:00)
>   - Cùng merchant: "Online Electronics"
>   - Giá trị giống nhau: $149.99
> - **Kết luận:** Bot tự động test card stolen, cần block ngay
>
> **User 7890 (nhiều amount lost nhất: 22.1M VND):**
> - 67 giao dịch, 11 bị fraud
> - Fraud rate: 16.4% (không cao lắm)
> - NHƯNG: Các giao dịch fraud có giá trị rất lớn ($800-$2,500)
> - **Kết luận:** High-value victim, cần tăng giới hạn cảnh báo
>
> ---
>
> **Users bị fraud ĐẦU TIÊN (new victim):**
>
> | User ID | Tổng GD | Fraud GD | First Fraud Time | Nhận xét |
> |---------|---------|----------|------------------|----------|
> | User AAA | 5 | 4 | 05/01 02:30 | 🚨 80% fraud ngay từ đầu → Card stolen before first use |
> | User BBB | 8 | 5 | 04/01 23:15 | 🚨 62.5% fraud → Compromised từ đầu |
> | User CCC | 12 | 7 | 05/01 03:00 | ⚠️ 58% fraud, giờ đêm khuya |
>
> ---
>
> **Scatter Chart insights:**
> - **Quadrant 1 (phải trên):** 8 users có >10 GD và fraud rate >20% → Ưu tiên review
> - **Quadrant 2 (trái trên):** 5 users có <10 GD nhưng fraud rate >50% → Card stolen ngay từ đầu
> - **Quadrant 3 (trái dưới):** Hầu hết users bình thường
> - **Quadrant 4 (phải dưới):** Users có nhiều GD nhưng fraud thấp → Trusted users
>
> **Biểu đồ:** [Table + Scatter Chart + Line Chart timeline]

---

## ❓ Câu 10: Từ các phân tích trên, hãy đề xuất cải tiến cho hệ thống để giảm gian lận hoặc tối ưu vận hành

### 🎯 Mục tiêu:
- Tổng hợp insights từ 9 câu trước
- Đề xuất **giải pháp cụ thể, khả thi** để giảm fraud và tối ưu hệ thống

### ✅ Câu trả lời (chia thành 3 phần: Phát hiện, Phòng chống, Tối ưu):

---

### 🔍 **PHẦN 1: CẢI TIẾN HỆ THỐNG PHÁT HIỆN FRAUD**

#### 1.1. Real-time Rule-based Blocking

**Dựa trên phân tích:**
- Câu 1: Giao dịch 2h-5h sáng có fraud rate 15-25%
- Câu 5: Users có >10 GD/giờ có 50%+ fraud
- Câu 7: Gas stations, Electronics có fraud rate 35%+

**Đề xuất:**

```python
# Rule 1: Time-based risk scoring
if transaction_hour in [2, 3, 4, 5]:
    risk_score += 30

# Rule 2: Velocity check
if user_transactions_last_hour > 10:
    risk_score += 40
    if user_transactions_last_hour > 15:
        BLOCK_TRANSACTION()

# Rule 3: High-risk merchant
if merchant_type in ['Gas Station', 'Online Electronics']:
    risk_score += 25
    REQUIRE_2FA()

# Rule 4: Weekend + Night
if is_weekend and transaction_hour in [23, 0, 1, 2, 3, 4]:
    risk_score += 35

# Rule 5: Geographic anomaly
if transaction_city != user_home_city:
    time_since_last_transaction = calculate_time_diff()
    if time_since_last_transaction < 2_hours:
        # Không thể từ New York đến Miami trong 2 giờ
        BLOCK_TRANSACTION()
```

**Ngưỡng quyết định:**
- Risk score < 30: Auto-approve
- Risk score 30-60: Require SMS OTP
- Risk score 60-80: Require 2FA + Phone call verification
- Risk score > 80: Auto-block + Alert fraud team

---

#### 1.2. Machine Learning Model Improvements

**Feature Engineering dựa trên insights:**

```python
# Từ Câu 1, 7: Time-based features
features.append('hour_of_day')
features.append('is_night_time')  # 2h-5h
features.append('is_weekend')
features.append('day_of_week')

# Từ Câu 5: Velocity features
features.append('transactions_last_1h')
features.append('transactions_last_24h')
features.append('avg_time_between_transactions')

# Từ Câu 2, 4: Location features
features.append('city_fraud_rate')  # Miami: 26.7%, Vegas: 23.7%
features.append('merchant_fraud_rate')
features.append('distance_from_home')

# Từ Câu 3, 6: Amount patterns
features.append('amount_category')  # LOW/MEDIUM/HIGH
features.append('amount_vs_user_avg_ratio')
features.append('is_round_amount')  # $100, $150 → suspicious

# Từ Câu 9: User history
features.append('user_fraud_history_count')
features.append('user_total_transactions')
features.append('card_age_days')
```

**Model stacking:**
```
Ensemble Model:
├─ XGBoost (40% weight) → Tốt cho categorical features
├─ Random Forest (30% weight) → Robust với outliers
├─ Neural Network (20% weight) → Capture complex patterns
└─ Rule-based (10% weight) → Domain knowledge
```

---

#### 1.3. Anomaly Detection cho Users

**Dựa trên Câu 5, 9:**

```python
# Isolation Forest để detect outlier users
from sklearn.ensemble import IsolationForest

user_features = {
    'transactions_per_hour': velocity,
    'fraud_rate': fraud_percentage,
    'avg_transaction_amount': avg_amount,
    'unique_merchants_count': unique_merchants,
    'unique_cities_count': unique_cities,
    'night_transactions_ratio': night_ratio
}

model = IsolationForest(contamination=0.05)  # 5% outliers
user_risk_score = model.predict(user_features)

# Users có score < -0.5 → Flagged for review
```

---

### 🛡️ **PHẦN 2: PHÒNG CHỐNG FRAUD CHỦ ĐỘNG**

#### 2.1. Merchant Risk Management

**Dựa trên Câu 3, 4, 7:**

**Blacklist merchants có fraud rate >30%:**
```
Gas Station XYZ: 39.3% fraud → BLOCK tạm thời
Online Electronics: 33.3% fraud → Require 2FA mọi GD
Jewelry Store ABC: 25.7% fraud → Enhanced monitoring
```

**Whitelist merchants uy tín:**
```
Walmart: 1.2% fraud → Fast-track approval
Starbucks: 0.8% fraud → No additional verification
Apple Store: 2.1% fraud → Normal flow
```

**Dynamic merchant scoring:**
```python
# Mỗi ngày recalculate
merchant_score = (
    fraud_rate * 0.4 +
    chargeback_rate * 0.3 +
    customer_complaints * 0.2 +
    industry_avg_comparison * 0.1
)

if merchant_score > 70:
    ACTION = "BLOCK_NEW_CARDS"  # Chỉ cho phép cards đã dùng trước đó
elif merchant_score > 50:
    ACTION = "REQUIRE_2FA"
```

---

#### 2.2. Geographic Fencing

**Dựa trên Câu 2, 4:**

**High-risk cities → Extra verification:**
```
Miami, FL (26.7% fraud):
- Require SMS OTP cho mọi giao dịch >$100
- Block giao dịch nếu user chưa từng đến Miami

Las Vegas, NV (23.7% fraud):
- Notify user trước khi approve (SMS: "Bạn có đang ở Vegas?")
- Limit $500/transaction cho lần đầu

Newark, NJ (21.2% fraud):
- Enhanced monitoring
```

**Travel notification system:**
```
Khi user book flight/hotel → Update whitelist cities tạm thời
VD: User book vé từ NY → Miami
→ Cho phép giao dịch ở Miami trong 7 ngày
→ Không cần SMS OTP
```

---

#### 2.3. Time-based Controls

**Dựa trên Câu 1, 7, 8:**

**Night-time restrictions (2h-5h):**
```python
if 2 <= transaction_hour <= 5:
    if amount > $200:
        REQUIRE_2FA()
    if merchant_type in HIGH_RISK_CATEGORIES:
        BLOCK_TRANSACTION()
        SEND_ALERT("Unusual night transaction blocked")
```

**Weekend extra verification:**
```python
if is_weekend:
    fraud_threshold *= 0.8  # Giảm ngưỡng từ $500 → $400

if is_weekend and transaction_hour in [23, 0, 1, 2]:
    REQUIRE_PHONE_CALL_VERIFICATION()
```

---

### ⚙️ **PHẦN 3: TỐI ƯU VẬN HÀNH HỆ THỐNG**

#### 3.1. Spark Streaming Performance Tuning

**Dựa trên kinh nghiệm vận hành:**

```python
# spark_streaming_consumer.py
spark = SparkSession.builder \
    .config("spark.sql.shuffle.partitions", "8")  # Tăng từ 4 → 8
    .config("spark.streaming.backpressure.enabled", "true")  # Auto throttling
    .config("spark.streaming.kafka.maxRatePerPartition", "100")  # Limit rate
    .config("spark.sql.adaptive.enabled", "true")  # Adaptive query execution
    .getOrCreate()

# Optimize deduplication state size
df_watermarked = df_filtered.withWatermark("transaction_datetime", "6 hours")
# Giảm từ 24h → 6h nếu không cần thiết
```

**Memory optimization:**
```python
# Checkpoint cleanup
spark.conf.set("spark.sql.streaming.minBatchesToRetain", "2")
spark.conf.set("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
```

---

#### 3.2. Airflow DAG Optimization

**Hiện tại:** Schedule mỗi 5 phút → Có thể overkill

**Đề xuất:**
```python
# dags/powerbi_streaming_dag.py

# Option 1: Dynamic schedule dựa trên data volume
from airflow.sensors.external_task_sensor import ExternalTaskSensor

def check_new_data_volume():
    # Chỉ push khi có >50 records mới
    # Nếu <50 records → Skip
    pass

# Option 2: Schedule linh hoạt
schedule_interval = {
    'weekday_peak': '*/3 * * * 1-5',      # 3 phút (T2-T6, 9h-18h)
    'weekday_off_peak': '*/10 * * * 1-5', # 10 phút (T2-T6, off-hours)
    'weekend': '*/15 * * * 6,0'           # 15 phút (T7, CN)
}
```

**Batch size optimization:**
```python
# Hiện tại: 10,000 rows/batch
# Đề xuất: Dynamic batch size
if total_rows < 100:
    batch_size = total_rows  # Push all at once
elif total_rows < 1000:
    batch_size = 500
else:
    batch_size = 2000  # Tăng từ 10k → 2k (faster, more frequent)
```

---

#### 3.3. Power BI Dashboard Optimization

**Tối ưu queries:**

```DAX
// Thay vì tính toán mọi lúc
// Tạo Calculated Table 1 lần:

Fraud Summary =
SUMMARIZE(
    RealTimeData,
    RealTimeData[Merchant_City],
    RealTimeData[transaction_hour],
    "Total Transactions", COUNT(RealTimeData[transaction_datetime]),
    "Fraud Count", CALCULATE(COUNT(RealTimeData[transaction_datetime]),
                               RealTimeData[Is_Fraud] = "Yes"),
    "Fraud Rate", DIVIDE([Fraud Count], [Total Transactions])
)

// Dùng Fraud Summary table cho visuals thay vì query raw data
```

**Incremental refresh:**
```
Settings → Dataset → Incremental refresh:
- Archive data >30 days
- Only refresh last 7 days
- Refresh frequency: 5 minutes
```

---

#### 3.4. Kafka Topic Partitioning Strategy

**Hiện tại:** 1 topic, partition by User ID

**Đề xuất:** Multi-topic architecture

```python
# Producer gửi vào 3 topics khác nhau:
TOPIC_HIGH_PRIORITY = "transactions_high_value"    # Amount > $500
TOPIC_NORMAL = "transactions_normal"               # $50 - $500
TOPIC_LOW_PRIORITY = "transactions_low_value"      # < $50

# Consumer riêng biệt cho từng topic
# → High-value transactions được process ưu tiên
# → Low-value có thể batch nhiều hơn
```

**Partitioning strategy:**
```python
# Thay vì partition by User
# → Partition by (User + City) hash
# → Transactions từ cùng user + city vào cùng partition
# → Tăng locality, giảm shuffle
```

---

#### 3.5. Monitoring & Alerting

**Real-time metrics dashboard (Grafana + Prometheus):**

```yaml
# Metrics cần track
metrics:
  - kafka_lag_per_partition          # Nếu >1000 → Scale up consumers
  - spark_processing_time_p99        # Nếu >5s → Optimize query
  - hdfs_write_throughput            # Monitor I/O bottleneck
  - fraud_detection_latency          # Target: <100ms
  - powerbi_push_success_rate        # Target: >99%
  - airflow_dag_run_duration         # Alert if >2 minutes
```

**Alerts:**
```yaml
# PagerDuty / Slack alerts
alerts:
  - name: "High Fraud Rate Spike"
    condition: fraud_rate_last_hour > 15%
    action: Alert fraud team + Block high-risk merchants

  - name: "Kafka Consumer Lag"
    condition: lag > 5000
    action: Auto-scale Spark cluster

  - name: "Power BI Push Failed"
    condition: push_failure_count > 3
    action: Check API key + Retry with exponential backoff
```

---

### 📊 **KẾT QUẢ KỲ VỌNG SAU KHI ÁP DỤNG**

| Metric | Hiện tại | Mục tiêu | Cải thiện |
|--------|----------|----------|-----------|
| **Fraud Detection Rate** | 75% | **95%** | +20% |
| **False Positive Rate** | 8% | **3%** | -62.5% |
| **Avg Detection Latency** | 2-4s | **<1s** | -66% |
| **Processing Throughput** | 30-120 GD/giờ | **200+ GD/giờ** | +67% |
| **Fraud Loss/Month** | $50,000 | **<$15,000** | -70% |
| **Customer Friction** | 12% GD bị block nhầm | **<4%** | -67% |

---

### 🎯 **ROADMAP TRIỂN KHAI (3 THÁNG)**

**Tháng 1: Quick Wins**
- ✅ Implement rule-based blocking cho night-time + high-risk merchants
- ✅ Setup Grafana monitoring dashboard
- ✅ Optimize Spark shuffle partitions
- ✅ Add geographic fencing cho Miami, Las Vegas

**Tháng 2: Core Improvements**
- ✅ Deploy ML model v2 với feature engineering mới
- ✅ Implement merchant risk scoring system
- ✅ Setup multi-topic Kafka architecture
- ✅ Power BI incremental refresh

**Tháng 3: Advanced Features**
- ✅ User anomaly detection với Isolation Forest
- ✅ Auto-scaling Spark cluster dựa trên Kafka lag
- ✅ A/B test rule-based vs ML-based blocking
- ✅ Feedback loop: Disputed transactions → Retrain model

---

### 📚 **TÀI LIỆU THAM KHẢO**

1. [Stripe Radar: Fraud Detection Best Practices](https://stripe.com/docs/radar)
2. [PayPal's Real-time Fraud Prevention](https://medium.com/paypal-tech/fighting-fraud-with-machine-learning-8b1b3c2c8e38)
3. [Uber's Streaming Fraud Detection](https://eng.uber.com/real-time-exactly-once-ad-event-processing/)
4. [Netflix's Anomaly Detection](https://netflixtechblog.com/rad-outlier-detection-on-big-data-d6b0494371cc)

---

**Tổng kết:**
Hệ thống fraud detection hiệu quả cần kết hợp:
- **Rules** (domain knowledge từ phân tích 9 câu trên)
- **Machine Learning** (detect complex patterns)
- **Real-time Processing** (Kafka + Spark Streaming)
- **Human-in-the-loop** (fraud team review edge cases)

**ROI dự kiến:**
- Giảm fraud loss: $35,000/month (~840M VND/tháng)
- Chi phí triển khai: ~$10,000 (one-time)
- **Payback period: <1 tháng**
