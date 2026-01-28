# 添加日期感知的平均銷售量計算功能 - 詳細設計方案

## 需求分析

### 核心需求
用戶希望在上載 Excel 檔案時，能夠選擇日期欄位，系統根據用戶選定的日期來動態計算：
1. **MTD（Month-To-Date）天數**：根據選定日期自動計算當月已經過的天數
2. **Avg Sold Qty 重新計算**：根據 MTD 天數重新計算平均銷售量，而不是固定的 60 天

### 範例說明
- **選定日期**：2026 年 1 月 27 日（系統預設為當日，使用者可修改）
- **MTD 天數**：26 天（1月1日到1月27日）
- **Last Month（上月）**：12 月，31 天
- **Last 2 Months（前兩個月）**：11 月，30 天

### 計算邏輯
假設用戶選定日期為 2026 年 1 月 27 日：

#### 原始計算公式（固定 60 天）
```
Avg_Daily_Sales = (Last_Month_Sold_Qty + Last_2_Month_Sold_Qty) / 60
```

#### 新的計算公式（加權平均，包含 MTD）
```
Avg_Daily_Sales = (MTD_Sold_Qty + Last_Month_Sold_Qty + Last_2_Month_Sold_Qty) /
                  (MTD_Days + Last_Month_Days + Last_2_Month_Days)
```

其中：
- `MTD_Days` = 當月已過天數（例如 1 月的 26 天）
- `Last_Month_Days` = 上月的總天數（例如 12 月的 31 天）
- `Last_2_Month_Days` = 前兩個月的總天數（例如 11 月的 30 天）
- `MTD_Sold_Qty` = 本月至今銷量（如果 Excel 有提供此欄位）

## 系統架構設計

### 1. 前端 UI 流程（Streamlit）

```
上傳檔案
    ↓
驗證必要欄位
    ↓
檢測日期欄位（自動或提示用戶選擇）
    ↓
顯示日期欄位選擇器（如果有多個日期欄位）
    ↓
用戶選擇目標日期（預設為今日）
    ↓
顯示計算參數摘要
    ↓
執行計算
```

### 2. 資料處理流程

#### 2.1 新增 DateFieldDetector 類別
**位置**：`core/data_processor.py`

```python
class DateFieldDetector:
    @staticmethod
    def detect_date_columns(df: pd.DataFrame) -> List[str]:
        """自動檢測日期欄位"""
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """取得指定年月的天數"""
    
    @staticmethod
    def calculate_mtd_days(date: datetime, year: int, month: int) -> int:
        """計算 MTD 天數"""
    
    @staticmethod
    def get_last_month_info(year: int, month: int) -> Tuple[int, int, int]:
        """取得上月年份、月份、天數"""
    
    @staticmethod
    def get_last_2_month_info(year: int, month: int) -> Tuple[int, int, int]:
        """取得前兩個月年份、月份、天數"""
```

#### 2.2 新增日期感知計算方法
**位置**：`core/calculator.py`

```python
class SafetyStockCalculator:
    def calculate_avg_daily_sales_with_date(
        self,
        last_month_qty: float,
        last_2_month_qty: float,
        mtd_days: int,
        last_month_days: int,
        last_2_month_days: int
    ) -> float:
        """基於實際日期計算平均日銷量"""
```

### 3. 後端資料結構更新

#### 3.1 Session State 新增項目
```python
st.session_state.date_field_name = None      # 選定的日期欄位名稱
st.session_state.selected_date = None        # 用戶選定的日期
st.session_state.mtd_days = None            # 計算出的 MTD 天數
st.session_state.last_month_days = None     # 上月天數
st.session_state.last_2_month_days = None   # 前兩個月天數
```

### 4. 計算步驟詳細流程

#### 第 1 步：日期欄位檢測與選擇
- 自動檢測 DataFrame 中的日期類型欄位
- 如果有多個日期欄位，提示用戶選擇
- 候選欄位可能包括：`date`, `Date`, `上傳日期`, `Launch Date`, `Order Date` 等

#### 第 2 步：日期值選擇
- 提供日期選擇器（預設為今日且時區為 UTC+8）
- 根據選定日期計算：
  - MTD 天數
  - 上月的年月和天數
  - 前兩個月的年月和天數

#### 第 3 步：平均銷售量重新計算
```
Given:
  - Last_Month_Sold_Qty = 上個月銷量
  - Last_2_Month_Sold_Qty = 前兩個月銷量
  - 選定日期：2026-01-27

Calculate:
  - MTD: 2026年1月1日～27日 = 26天
  - Last Month: 2025年12月 = 31天
  - Last 2 Months: 2025年11月 = 30天

Then:
  Avg_Daily_Sales = (Last_Month_Sold_Qty / 31 + Last_2_Month_Sold_Qty / 30) / 2
```

#### 第 4 步：執行安全庫存計算
- 使用新的 Avg_Daily_Sales 代替固定的 60 天計算
- 其餘計算邏輯保持不變

## 實施計劃

### 修改文件清單

#### 1. `core/constants.py`
- 新增日期相關常數

#### 2. `core/data_processor.py`
- 新增 `DateFieldDetector` 類別
- 新增日期欄位檢測方法
- 新增日期工具方法（月份計算、天數計算等）

#### 3. `core/calculator.py`
- 新增 `calculate_avg_daily_sales_with_date()` 方法
- 修改 `calculate_safety_stock()` 方法簽名以支持日期參數

#### 4. `app.py`
- 在文件上傳後新增「日期欄位與日期選擇」章節
- 新增 UI 元件：日期欄位選擇下拉菜單
- 新增 UI 元件：日期選擇器
- 新增計算參數摘要顯示
- 修改計算流程以傳遞日期相關參數

### UI 元件設計

#### 檔案上傳後的新增流程

```
📤 上傳資料檔案
  [檔案上傳控制項]

📋 查看原始資料
  [摺疊面板，顯示資料預覽]

---

📅 日期設定與計算參數（新增部分）
  ├─ 選擇參考日期
  │  └─ [日期選擇器] 選擇參考日期（預設系統當日：2026-01-27）
  │
  ├─ 自動檢測日期欄位
  │  └─ 與選定日期對應的 MTD/Last Month/Last 2 Months
  │
  ├─ 📊 計算參數摘要（詳細顯示）
  │  ├─ 選定日期：2026-01-27
  │  ├─ 當月（1月）：26 天
  │  ├─ 上月（12月）：31 天
  │  ├─ 前兩月（11月）：30 天
  │  ├─ 計算公式說明
  │  │  └─ Avg_Daily_Sales = (MTD_Qty + Last_Month_Qty + Last_2_Month_Qty) /
  │  │                       (MTD_Days + Last_Month_Days + Last_2_Month_Days)
  │  ├─ 數據將從 Article 中的欄位提取
  │  └─ ✅ 已驗證數據完整性
  │
  └─ 💡 計算詳細流程演示
     └─ 範例：(26 + 100 + 90) / (26 + 31 + 30) = 216 / 87 ≈ 2.48

---

🎯 SKU 目標數量分配
  [原有的 SKU 編輯器]

---

🚀 開始計算
  [計算按鈕]
```

## 技術細節

### 1. 日期計算函數

```python
from datetime import datetime, timedelta
import calendar

def get_days_in_month(year: int, month: int) -> int:
    """取得指定年月的天數"""
    return calendar.monthrange(year, month)[1]

def calculate_mtd_days(date: datetime.date, year: int, month: int) -> int:
    """
    計算 MTD 天數
    例：2026-01-27 的 MTD = 27 天
    """
    if date.year == year and date.month == month:
        return date.day
    else:
        raise ValueError("選定日期必須在設定的月份內")

def get_last_month_info(year: int, month: int) -> Tuple[int, int, int]:
    """
    取得上月信息
    返回：(上月年份, 上月月份, 上月天數)
    例：(2026, 1) → (2025, 12, 31)
    """
    if month == 1:
        return year - 1, 12, 31
    else:
        return year, month - 1, get_days_in_month(year, month - 1)

def get_last_2_month_info(year: int, month: int) -> Tuple[int, int, int]:
    """
    取得前兩個月信息
    返回：(前兩月年份, 前兩月月份, 前兩月天數)
    例：(2026, 1) → (2025, 11, 30)
    """
    if month == 1:
        return year - 1, 11, get_days_in_month(year - 1, 11)
    elif month == 2:
        return year - 1, 12, 31
    else:
        return year, month - 2, get_days_in_month(year, month - 2)
```

### 2. 日期欄位自動檢測

```python
def detect_date_columns(df: pd.DataFrame) -> List[str]:
    """
    自動檢測日期欄位
    查找列名中包含日期相關詞彙或資料類型為 datetime 的欄位
    """
    date_keywords = ['date', 'time', '日期', '時間', '日', '時']
    detected_columns = []
    
    # 檢測資料類型
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            detected_columns.append(col)
        elif col.lower() in date_keywords or any(kw in col.lower() for kw in date_keywords):
            # 嘗試將該欄位轉換為日期類型
            try:
                pd.to_datetime(df[col])
                detected_columns.append(col)
            except:
                pass
    
    return detected_columns
```

### 3. 新的平均銷售量計算

```python
def calculate_avg_daily_sales_with_date(
    mtd_qty: float,
    last_month_qty: float,
    last_2_month_qty: float,
    mtd_days: int,
    last_month_days: int,
    last_2_month_days: int
) -> float:
    """
    基於實際日期計算平均日銷量（加權平均）
    
    公式：
    Avg_Daily_Sales = (MTD_Sold_Qty + Last_Month_Sold_Qty + Last_2_Month_Sold_Qty) /
                      (MTD_Days + Last_Month_Days + Last_2_Month_Days)
    
    例：
    Avg_Daily_Sales = (26 + 100 + 90) / (26 + 31 + 30) = 216 / 87 ≈ 2.48
    """
    total_days = mtd_days + last_month_days + last_2_month_days
    
    if total_days <= 0:
        return 0.0
    
    total_qty = mtd_qty + last_month_qty + last_2_month_qty
    avg_daily_sales = total_qty / total_days
    
    return round(avg_daily_sales, 2)
```

## 資料流變更

### 修改前的流程
```
File Upload
  → DataProcessor.load_data()
  → DataProcessor.validate_required_columns()
  → Display data preview
  → User input SKU targets
  → calculate_safety_stock(df, settings, sku_targets)
    → SafetyStockCalculator.calculate_avg_daily_sales(last_month, last_2_month)
      → Avg_Daily_Sales = (last_month + last_2_month) / 60
    → [Rest of calculation]
```

### 修改後的流程
```
File Upload
  → DataProcessor.load_data()
  → DataProcessor.validate_required_columns()
  → [NEW] Display date picker (default: today 2026-01-27)
  → [NEW] Calculate MTD, Last Month, Last 2 Months days
  → [NEW] Extract MTD_Sold_Qty from data (if available)
  → [NEW] Display detailed calculation parameters summary
  → Display data preview
  → User input SKU targets
  → calculate_safety_stock(
      df, settings, sku_targets,
      selected_date,
      mtd_qty, mtd_days,
      last_month_days, last_2_month_days
    )
    → SafetyStockCalculator.calculate_avg_daily_sales_with_date(
        mtd_qty, last_month_qty, last_2_month_qty,
        mtd_days, last_month_days, last_2_month_days
      )
      → Avg_Daily_Sales = (mtd_qty + last_month_qty + last_2_month_qty) /
                          (mtd_days + last_month_days + last_2_month_days)
    → [Rest of calculation remains the same]
```

## 輸出結果變更

### 新增欄位
計算結果中新增以下欄位（用於說明/審計）：
- `Selected_Date`: 用戶選定的參考日期（例：2026-01-27）
- `MTD_Days`: 計算出的 MTD 天數（例：26）
- `Last_Month_Days`: 上月天數（例：31）
- `Last_2_Month_Days`: 前兩月天數（例：30）
- `Calculation_Method`: 計算方法標識（固定值："Date-Based Weighted Average"）

### Notes 欄位更新
原有的 `Notes` 欄位將包含以下新增信息：
```
計算步驟：
0. 日期感知計算模式
   - 選定參考日期：2026-01-27
   - 當月(1月)天數：26天
   - 上月(12月)天數：31天
   - 前兩月(11月)天數：30天

1. 平均日銷量（加權平均，基於實際天數）
   - MTD 銷量 = 26
   - 上月銷量 = 100
   - 前兩月銷量 = 90
   - 平均日銷量 = (26 + 100 + 90) / (26 + 31 + 30) = 216 / 87 = 2.48

2. 前置時間 = 7 天 (Supply Source: 1)
...
```

## 驗證清單

### 計算驗證
- [ ] 驗證 2026-01-27 的 MTD = 26 天（1月有31天）
- [ ] 驗證上月（12月）= 31 天
- [ ] 驗證前兩月（11月）= 30 天
- [ ] 驗證加權平均公式計算正確
  - [ ] Avg = (MTD_Qty + Last_Month_Qty + Last_2_Month_Qty) / (26 + 31 + 30)
- [ ] 驗證使用提供的 Test_26Jan2026.XLSX 測試

### 功能驗證
- [ ] 日期選擇器預設為系統當日（2026-01-27）
- [ ] 用戶可修改日期選擇
- [ ] 無需日期欄位檢測（簡化流程）
- [ ] 計算參數摘要詳細顯示計算公式
- [ ] 計算結果中的新欄位正確填充
- [ ] 追蹤計算方式（"Date-Based Weighted Average"）

### UI 驗證
- [ ] 日期選擇介面清晰易用
- [ ] 參數摘要詳細顯示計算過程
- [ ] 數據驗證提示清楚
- [ ] 錯誤訊息清楚明確

## 風險評估

### 風險 1：日期欄位自動檢測失敗
- **風險等級**：中
- **緩解方案**：提供手動日期欄位選擇選項

### 風險 2：資料中沒有日期欄位
- **風險等級**：低
- **緩解方案**：顯示警告信息，允許用戶使用系統參考日期

### 風險 3：月份天數計算錯誤
- **風險等級**：低
- **緩解方案**：使用標準庫 `calendar.monthrange()` 確保準確性

### 風險 4：向後兼容性問題
- **風險等級**：中
- **緩解方案**：日期參數應設為可選，默認使用原有的 60 天計算

## 後續考慮

1. **功能完整性**：
   - ✅ 已移除日期欄位自動檢測（簡化流程）
   - ✅ 通過日期選擇器實現用戶控制
   - ✅ 支持上傳時的日期選擇
   - ✅ 結果中追蹤計算方式

2. **性能考量**：
   - 大型 Excel 檔案的計算性能
   - 考慮快取月份天數計算結果

3. **擴展性**：
   - 未來支援用戶自定義計算公式
   - 未來支援不同的日期區間（每週、每季度等）
   - 未來支援多個時間基準點的對比

4. **文檔與用戶教育**：
   - 更新首頁使用說明，新增日期感知計算方式
   - 在計算參數摘要中提供公式說明
   - 在 Notes 欄位中詳細記錄計算步驟
   - 在首頁添加計算方式選擇說明
