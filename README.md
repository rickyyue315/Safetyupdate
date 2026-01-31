# 安全(緩衝)庫存計算機 v2.5
# Safety(Buffer) Stock Calculation v2.5

## 📋 專案簡介

本系統根據實際可用資料欄位及商業限制，計算合理的安全庫存建議值。系統確保重點店（高階 Shop Class）擁有較高服務水準，同時滿足 MOQ 最小訂購量要求，並允許使用者自訂安全庫存天數上限（7–14 天）。

**v2.5 新增功能** 🆕：
- ✅ **店舖類型配置模式**：根據店舖區域(HK/MO) + 店舖等級(A/B/C/D) + 貨場面積(XL/L/M/S/XS)查表獲取固定安全庫存數量，適合統一配貨標準場景

**v2.3 新增功能**：
- ✅ MCH2 最低安全庫存要求：當 MCH2 欄位為 "0302" 時，根據 Shop Class 應用最低安全庫存要求（AA/A1/A2/A3 ≥ 12件，B1/B2 ≥ 10件，C1/C2/D1 ≥ 6件）

**v2.2 新增功能**：
- ✅ Launch Date 驗證功能：根據商品實際上市日期調整安全庫存計算，當商品上市時間短於計算週期時，使用實際天數計算平均日銷量，提供更精確的安全庫存建議
- ✅ Target Qty 模式：支援直接使用輸入資料中的 `Target Qty` 作為安全庫存，跳過公式計算
- ✅ Target Safety Stock 模式：支援輸入 SKU 總目標數量，系統自動按比例分配至各店舖

## ✨ 核心功能

- **智能計算**: 根據平均日銷量、前置時間和合併因素計算安全庫存
- **店舖類型配置模式** 🆕: 根據店舖區域、等級和面積查表獲取固定安全庫存，適合統一配貨標準
- **MCH2 最低安全庫存要求**: 當 MCH2 欄位為 "0302" 時，根據 Shop Class 應用最低安全庫存要求（AA/A1/A2/A3 ≥ 12件，B1/B2 ≥ 10件，C1/C2/D1 ≥ 6件）
- **Launch Date 驗證**: 根據商品實際上市日期調整計算邏輯，當商品上市時間短於計算週期時，使用實際天數計算平均日銷量，提供更精確的安全庫存建議
- **MOQ 約束**: 自動套用最小訂購量約束（支援乘數模式和加 1 模式）
- **天數上限**: 支援自訂安全庫存天數上限（7-14 天）
- **Target Qty 模式**: 支援直接使用輸入資料中的 `Target Qty` 作為安全庫存，跳過公式計算
- **Target Safety Stock 模式**: 支援輸入 SKU 總目標數量，系統自動按比例分配至各店舖
- **多種輸入**: 支援 CSV 和 Excel 檔案輸入
- **結果匯出**: 可匯出計算結果為 Excel 或 CSV 格式，包含詳細的 SKU 統計摘要
- **設定管理**: 支援全域設定和按 Shop Class 設定天數上限
- **日期感知計算**: 支援根據用戶選定的參考日期，自動計算 MTD 天數、上月天數、前兩月天數，並使用加權平均公式計算平均日銷量

## 📐 計算公式

### 1. 店舖類型配置模式 (Shop Type Configuration Mode) 🆕
- **查表邏輯**: 根據「區域 (HK/MO)」+「店舖等級 (A/B/C/D)」+「貨場面積 (XL/L/M/S/XS)」查詢配置表
- **固定配置**: 使用預先設定的固定安全庫存數量，不使用公式計算
- **必要欄位**: `Region` (區域), `Class` (店舖等級), `Shop Size` (貨場面積)
- **配置範例**:
  - HK A級店鋪: 18件
  - HK B級店鋪 L: 18件, M/S/XS: 12件
  - MO A級店鋪: 24件
- **詳細說明**: 參考 [店舖類型配置模式快速指南](SHOP_TYPE_MODE_QUICK_GUIDE.md)

### 2. 標準模式 (Standard Mode)
1. **初步安全庫存**: `SS_preliminary = Avg_Daily_Sales × √Lead_Time_Days × MF`
2. **套用 MOQ 約束**: `SS_after_MOQ = max(SS_preliminary, MOQ × multiplier)`
3. **套用天數上限**: `Suggested_Safety_Stock = min(SS_after_MOQ, Avg_Daily_Sales × Max_Days)`
4. **套用 MCH2 最低要求**（若 MCH2 = "0302"）: `Suggested_Safety_Stock = max(Suggested_Safety_Stock, MCH2_Minimum_Required)`
   - **最低要求映射**:
     - Shop Class AA, A1, A2, A3: 12 件
     - Shop Class B1, B2: 10 件
     - Shop Class C1, C2, D1: 6 件

### 3. 日期感知計算模式 (Date-Based Calculation Mode)
1. **日期參數計算**: 根據用戶選定的參考日期，自動計算：
   - MTD 天數（當月已過天數）
   - 上月天數（12月 = 31 天）
   - 前兩月天數（11月 = 30 天）
2. **加權平均日銷量**: 使用實際月份天數計算
   - **計算公式**:
     - **標準模式（60天）**: `Avg_Daily_Sales = (Last_Month_Sold_Qty + Last_2_Month_Sold_Qty) / 60`
     - **日期感知模式（加權平均）**: `Avg_Daily_Sales = (MTD_Sold_Qty + Last_Month_Sold_Qty + Last_2_Month_Sold_Qty) / (MTD_Days + Last_Month_Days + Last_2_Month_Days)`
   - **範例**（2026-01-27）：
     - MTD 天數 = 26
     - 上月天數 = 31（12月）
     - 前兩月天數 = 30（11月）
     - Avg = (26 + 100 + 90) / (26 + 31 + 30) = 216 / 87 ≈ 2.48

### 3. Launch Date 影響計算
當商品提供 Launch Date（上市日期）時，系統會檢測是否需要調整計算邏輯：
- **啟動條件**: 當 Launch Date 到參考日期的實際天數 **少於** 計算總天數時
- **計算公式**:
  ```
  days_since_launch = (參考日期 - Launch Date).days + 1
  Avg_Daily_Sales = (MTD_Qty + Last_Month_Qty + Last_2_Month_Qty) / days_since_launch
  ```
- **範例**（參考日期 2026-01-26，Launch Date 2026-01-21）：
  - 標準總天數 = 87 天（26 + 31 + 30）
  - 實際天數 = 6 天（1/21 到 1/26）
  - 由於 6 < 87，使用實際天數計算
  - Avg = (20 + 100 + 150) / 6 = 270 / 6 = 45.0
- **Notes 提示**: 系統會在 Notes 欄位中顯示「Launch Date 影響計算，只計算Launch Date到參考日期的實際天數」

### 2. Target Qty 模式
- `Suggested_Safety_Stock = Target Qty` (直接使用輸入值)

### 3. Target Safety Stock 模式
- 按店舖等級 (Class) 權重比例分配：
  - Class A (AA, A1, A2, A3)：權重 A
  - Class B (B1, B2)：權重 B
  - Class C (C1, C2)：權重 C
  - Class D (D1)：權重 D
- 預設權重：A=3, B=2, C=1, D=1（可在系統設定中自訂）
- 分配邏輯：
  1. 計算總權重：`Total_Weight = Σ Weight_i`
  2. 計算分配係數：`Factor = SKU_Total_Target / Total_Weight`
  3. 初步分配：`Allocated_i = floor(Weight_i × Factor)`
  4. 計算餘數：`Remainder = SKU_Total_Target - Σ Allocated_i`
  5. 將餘數分配給小數部分最大的店舖（每個店舖加 1）
  6. 確保總和等於目標數量
- 系統會自動處理分配餘數，確保總和等於目標數量。

## 🛠️ 技術堆疊

- **前端框架**: Streamlit
- **後端語言**: Python 3.11
- **資料處理**: Pandas, NumPy
- **容器化**: Docker, Docker Compose

## 📁 專案結構

```
Kilo Safety Stock Calculate/
├── app.py                          # Streamlit 主應用程式
├── requirements.txt                # Python 套件依賴
├── README.md                       # 專案說明文件
├── Dockerfile                      # Docker 容器化設定
├── docker-compose.yml              # Docker Compose 設定
├── config/
│   ├── __init__.py
│   └── settings.py                 # 系統設定管理
├── core/
│   ├── __init__.py
│   ├── calculator.py               # 核心計算邏輯
│   ├── data_processor.py           # 資料處理
│   └── constants.py               # 常數定義（MF 表等）
├── ui/
│   ├── __init__.py
│   ├── pages/                     # Streamlit 頁面
│   └── components/                # UI 元件
├── utils/
│   ├── __init__.py
│   ├── validators.py               # 資料驗證
│   └── exporters.py                # 匯出功能
├── data/
│   ├── input/                     # 輸入資料範例
│   │   └── sample_input.csv
│   └── output/                    # 輸出資料目錄
├── tests/                         # 測試檔案
└── docs/                          # 文件目錄
```

## 🚀 快速開始

### 方法一：使用 Python 虛擬環境

1. **建立虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

2. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

3. **執行應用程式**
   ```bash
   streamlit run app.py
   ```

4. **開啟瀏覽器**
   
   瀏覽器會自動開啟至 `http://localhost:8501`

### 方法二：使用 Docker

1. **建置 Docker 映像**
   ```bash
   docker build -t safety-stock-calculator .
   ```

2. **執行容器**
   ```bash
   docker run -p 8501:8501 -v $(pwd)/data:/app/data safety-stock-calculator
   ```

3. **使用 Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **開啟瀏覽器**
   
   訪問 `http://localhost:8501`

## 📊 輸入資料格式

您的資料檔案必須包含以下欄位：

| 欄位名稱 | 說明 | 範例 |
|------------|------|------|
| Article | 商品編號 | ART001 |
| Site | 門市代碼 | S001 |
| Class | 店舖等級 | AA, A1, A2, A3, B1, B2, C1, C2, D1 |
| Last Month Sold Qty | 上個月銷量 | 120 |
| Last 2 Month Sold Qty | 前兩個月銷量總和 | 240 |
| Supply Source | 供應來源代碼 | 1, 2, 4 |
| MOQ | 最小訂購量 | 10 |
| MCH2 | MCH2 值（必須欄位） | 0302 |
| Target Qty | 目標數量 (可選) | 50 |
| Launch Date | 商品上市日期 (可選，格式：yyyy-MM-dd) | 2026-01-21 |

您可以下載 [`data/input/sample_input.csv`](data/input/sample_input.csv) 作為參考。

## ⚙️ 系統設定

### 全域設定

- **安全庫存天數上限**: 7-14 天（預設 14 天）
- **MOQ 約束乘數**: > 0（預設 1.25）
- **MOQ 約束模式**: 
  - `multiplier`: 乘數模式（預設）
  - `add_one`: 加 1 模式
- **Target Qty 模式**: 啟用後優先使用 `Target Qty` 欄位

### 按 Shop Class 設定

可以為不同的 Shop Class 設定不同的天數上限：
- AA, A1, A2, A3, B1, B2, C1, C2, D1
- 範圍：7-14 天
- 留空則使用全域設定

### Class 權重設定

用於 Target Safety Stock 模式的 SKU 目標數量分配：
- **Class A (AA, A1, A2, A3)**：權重 A（預設 3）
- **Class B (B1, B2)**：權重 B（預設 2）
- **Class C (C1, C2)**：權重 C（預設 1）
- **Class D (D1)**：權重 D（預設 1）
- 權重越大，分配的數量越多
- 可在系統設定中自訂各類別的權重（範圍：1-100）
- 預設分配比例：A : B : C : D = 3 : 2 : 1 : 1

## 📤 使用說明

1. **上傳資料檔案**
   - 在「計算」頁面上傳您的 CSV 或 Excel 檔案
   - 系統會自動驗證檔案格式

2. **調整系統設定**（可選）
   - 在側邊欄調整全域天數上限
   - 選擇 MOQ 約束模式
   - 設定 MOQ 乘數
   - 為特定 Shop Class 設定天數上限（可選）

3. **設定 SKU 目標數量**（可選）
   - 在「SKU 目標數量分配」表格中輸入各 SKU 的總目標數量
   - 系統會按店舖等級 (Class) 權重比例自動分配：
     - Class A (AA, A1, A2, A3)：權重 A（預設 3）
     - Class B (B1, B2)：權重 B（預設 2）
     - Class C (C1, C2)：權重 C（預設 1）
     - Class D (D1)：權重 D（預設 1）
   - 可在系統設定中自訂各類別的權重
   - 若輸入 0 則使用標準計算公式

4. **執行計算**
   - 點擊「開始計算」按鈕
   - 系統會處理所有記錄並顯示結果

4. **查看結果**
   - 查看詳細計算結果表格
   - 查看統計摘要
   - 分析約束記錄

5. **匯出結果**（如需要）
   - 匯出為 Excel 格式（包含結果和摘要工作表）
   - 匯出為 CSV 格式

## 📈 輸出結果說明

計算結果包含以下欄位：

| 欄位名稱 | 說明 |
|------------|------|
| Article | 商品編號 |
| Site | 門市代碼 |
| Class | 店舖等級 |
| Avg_Daily_Sales | 平均日銷量 |
| Lead_Time_Days | 前置時間（天數） |
| MF_Used | 使用的合併因素 |
| MF_Service_Level | 服務水準（%） |
| Preliminary_SS | 初步安全庫存 |
| SS_after_MOQ | 套用 MOQ 約束後的安全庫存 |
| User_Max_Days_Applied | 應用的天數上限 |
| Suggested_Safety_Stock | 建議安全庫存（最終值） |
| Constraint_Applied | 約束類型（MOQ / 天數上限 / MCH2 / 兩者 / 三者 / Target Qty / Target Safety Stock） |
| Safety_Stock_Days | 最終值可支撐天數 |
| MCH2 | MCH2 值 |
| MCH2_Minimum_Required | MCH2 最低要求值（若不適用則為 0） |
| MCH2_Minimum_SS_Applied | 是否應用了 MCH2 約束 (True/False) |
| Target_Qty_Used | 是否使用了 Target Qty (True/False) |
| Calculation_Mode | 計算模式 (Standard / Target Qty / Target Safety Stock) |
| Notes | 計算說明，包含 Launch Date 影響提示（如適用） |

## 🔧 開發指南

### 安裝開發依賴

```bash
pip install -r requirements.txt
```

### 執行測試

```bash
pytest tests/ -v --cov=core --cov=utils
```

### 程式碼格式化

```bash
black .
```

### 程式碼檢查

```bash
flake8 .
```

## 📝 合併因素（MF）對照表

| Shop Class | MF 值 | 服務水準 |
|-----------|---------|----------|
| AA | 2.58 | 99.5% |
| A1 | 2.33 | 99.0% |
| A2 | 2.05 | 98.0% |
| A3 | 1.88 | 97.0% |
| B1 | 1.75 | 96.0% |
| B2 | 1.645 | 95.0% |
| C1 | 1.555 | 94.0% |
| C2 | 1.48 | 93.0% |
| D1 | 1.28 | 90.0% |

## 🔮 未來擴展方向

### 短期擴展（v1.1）
- [ ] 支援按 Shop Class 設定不同的天數上限
- [ ] 加入計算歷史紀錄功能
- [ ] 提供更多匯出格式（PDF、JSON）
- [ ] 加入資料視覺化圖表

### 中期擴展（v2.1）
- [ ] 引入銷量標準差計算，升級為完整統計模型
- [ ] 加入季節性/促銷調整係數
- [ ] 支援資料庫連接（MySQL、PostgreSQL）
- [ ] 加入排程自動計算功能

### 長期擴展（v3.0）
- [ ] 結合現有庫存與在途量，產出建議訂貨量
- [ ] 支援多層級天數上限設定
- [ ] 加入機器學習模型預測銷量
- [ ] 提供多使用者權限管理
- [ ] 支援多語言介面

## 🐛 故障排除

### 常見問題

**Q: 上傳檔案時出現錯誤？**
A: 請檢查檔案格式是否為 CSV、.xlsx 或 .xls，並確認包含所有必要欄位。

**Q: 計算結果不合理？**
A: 請檢查輸入資料是否正確，特別是銷量和 MOQ 值。

**Q: Docker 容器無法啟動？**
A: 請確認 Docker 已正確安裝並執行，檢查端口 8501 是否被佔用。

## 📄 授權

本專案採用 MIT 授權。

## 👨‍💻 貢獻

歡迎提交 Issue 和 Pull Request！

## 📧 聯絡方式

如有任何問題或建議，請聯繫專案維護者。

---

**注意**: 本系統僅提供建議值，實際庫存管理應根據具體業務情況進行調整。

---

**Safety (Buffer) Stock Calculate v2.3 - For RP team (Build up by Ricky Yue)**
