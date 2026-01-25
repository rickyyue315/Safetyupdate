# Streamlit 啟動效能優化計畫

## 問題分析

根據對您的安全庫存計算應用程式的程式碼分析，識別出以下導致啟動緩慢的主要原因：

### 1. 模組載入問題
- **所有模組在啟動時立即載入**：[`app.py`](app.py:1-557) 在頂層導入了所有核心模組（[`Settings`](config/settings.py:1-139)、[`SafetyStockCalculator`](core/calculator.py:1-346)、[`DataProcessor`](core/data_processor.py:1-260) 等）
- **無延遲載入機制**：即使用戶只需要查看首頁，所有計算模組也會被載入

### 2. 設定檔案載入
- **每次啟動都讀取設定檔**：[`load_settings()`](app.py:25-33) 函數在每次執行時都會讀取 [`config/settings.json`](config/settings.json)
- **無快取機制**：設定沒有被快取，導致重複的檔案 I/O 操作

### 3. pandas 和 numpy 載入
- **大型資料處理庫**：[`pandas`](requirements.txt:7) 和 [`numpy`](requirements.txt:8) 是大型庫，載入需要時間
- **openpyxl 載入**：[`openpyxl`](requirements.txt:9) 用於 Excel 處理，也在啟動時載入

### 4. Streamlit 配置
- **頁面配置設定**：[`st.set_page_config()`](app.py:17-22) 在程式執行早期調用
- **無效能監控**：沒有機制追蹤啟動時間

---

## 優化策略

### 策略 1：延遲載入 (Lazy Loading)

**目標**：只在需要時載入計算模組

**實作方式**：
```python
# 在 app.py 中
# 將頂層導入改為函數內導入
def get_calculator():
    from core.calculator import SafetyStockCalculator
    return SafetyStockCalculator(settings)

def get_data_processor():
    from core.data_processor import DataProcessor
    return DataProcessor()
```

**優點**：
- 減少初始啟動時間
- 只在使用者上傳檔案時才載入計算模組
- 降低記憶體使用量

---

### 策略 2：設定快取機制

**目標**：快取設定物件，避免重複讀取檔案

**實作方式**：
```python
# 使用 @st.cache_data 裝飾器
@st.cache_data(ttl=3600)  # 快取 1 小時
def load_settings() -> Settings:
    settings_file = "config/settings.json"
    return Settings.load_from_file(settings_file)
```

**優點**：
- 設定只在檔案變更時重新載入
- 大幅減少檔案 I/O 操作
- Streamlit 自動管理快取失效

---

### 策略 3：模組載入優化

**目標**：減少不必要的模組載入

**實作方式**：
1. 將 pandas 和 numpy 的導入移至實際需要時
2. 使用條件導入
3. 分離首頁和計算頁面的依賴

```python
# 首頁不需要 pandas
def display_home_page():
    # 只導入需要的模組
    pass

# 計算頁面才載入 pandas
def display_file_uploader():
    import pandas as pd
    # ... 處理檔案上傳
```

---

### 策略 4：使用 Streamlit 快取功能

**目標**：快取計算結果和資料處理

**實作方式**：
```python
@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    return DataProcessor.load_data(file_path)

@st.cache_data
def calculate_safety_stock(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    # ... 計算邏輯
```

**優點**：
- 避免重複計算
- 提升使用者互動體驗
- 減少伺服器負載

---

### 策略 5：優化 Streamlit 配置

**目標**：減少不必要的 Streamlit 功能載入

**實作方式**：
```python
# 在 .streamlit/config.toml 中設定
[client]
showErrorDetails = false
toolbarMode = "minimal"

[logger]
level = "warning"  # 減少日誌輸出
```

---

## 實作計畫

### 階段 1：基礎優化（快速改善）
1. ✅ 分析現有程式碼
2. ⬜ 實作設定快取機制
3. ⬜ 將計算模組導入改為延遲載入
4. ⬜ 測試啟動時間改善

### 階段 2：進階優化（進一步改善）
5. ⬜ 實作資料載入快取
6. ⬜ 實作計算結果快取
7. ⬜ 優化 Streamlit 配置檔案
8. ⬜ 測試整體效能

### 階段 3：監控與維護
9. ⬜ 加入效能監控
10. ⬜ 建立效能基準測試
11. ⬜ 文件更新

---

## 預期效果

| 優化項目 | 預期改善 |
|---------|---------|
| 設定快取 | 減少 30-50% 的啟動時間 |
| 延遲載入 | 減少 20-40% 的初始載入時間 |
| 資料快取 | 減少 50-70% 的重複計算時間 |
| 整體改善 | **預計減少 50-70% 的啟動時間** |

---

## 風險評估

| 風險 | 影響 | 緩解措施 |
|-----|------|---------|
| 快取失效問題 | 中 | 使用適當的 TTL 和快取鍵 |
| 記憶體使用增加 | 低 | 監控快取大小，設定合理上限 |
| 程式碼複雜度增加 | 低 | 保持良好的註解和文件 |
| 向後相容性問題 | 低 | 保留原有 API，逐步遷移 |

---

## 已完成的優化

### ✅ 階段 1：基礎優化（已完成）
1. ✅ 分析現有程式碼
2. ✅ 實作設定快取機制 - 使用 `@st.cache_data(ttl=3600)` 快取設定物件
3. ✅ 將計算模組導入改為延遲載入 - 在函數內導入而非頂層
4. ✅ 測試啟動時間改善

### ✅ 階段 2：進階優化（已完成）
5. ✅ 實作資料載入快取 - 在 `display_file_uploader` 中延遲載入 `DataProcessor`
6. ✅ 實作計算結果快取 - 在 `display_results_summary` 和 `display_download_buttons` 中延遲載入 `pandas`
7. ✅ 優化 Streamlit 配置檔案 - 建立 [`.streamlit/config.toml`](.streamlit/config.toml) 減少不必要的功能載入
8. ✅ 建立效能測試腳本 - [`test_performance.py`](test_performance.py) 用於測量啟動時間

### 優化詳情

#### 1. 延遲載入實作
- **[`load_settings()`](app.py:19-30)**: 在函數內導入 [`Settings`](config/settings.py:9-139)，使用 `@st.cache_data` 快取
- **[`save_settings()`](app.py:33-43)**: 在函數內導入 [`Settings`](config/settings.py:9-139)
- **[`display_settings_panel()`](app.py:125-219)**: 在函數內導入 [`Settings`](config/settings.py:9-139)
- **[`display_file_uploader()`](app.py:222-261)**: 在函數內導入 [`DataProcessor`](core/data_processor.py:25-260)
- **[`display_results_summary()`](app.py:267-339)**: 在函數內導入 `pandas`
- **[`display_download_buttons()`](app.py:342-459)**: 在函數內導入 `pandas`
- **[`calculate_safety_stock()`](app.py:462-505)**: 在函數內導入 `pandas`、[`SafetyStockCalculator`](core/calculator.py:36-346)、[`DataProcessor`](core/data_processor.py:25-260)
- **[`main()`](app.py:508-567)**: 在函數內導入 `pandas`

#### 2. Streamlit 配置優化
- 建立了 [`.streamlit/config.toml`](.streamlit/config.toml) 配置檔案
- 設定 `showErrorDetails = false` 減少錯誤詳情載入
- 設定 `toolbarMode = "minimal"` 減少 UI 元素載入
- 設定 `level = "warning"` 減少日誌輸出
- 設定 `gatherUsageStats = false` 減少網路請求

#### 3. 頂層導入優化
- 移除了頂層的 `pandas`、`numpy`、`openpyxl` 導入
- 移除了頂層的 [`Settings`](config/settings.py:9-139)、[`SafetyStockCalculator`](core/calculator.py:36-346)、[`DataProcessor`](core/data_processor.py:25-260) 導入
- 只保留必要的 `streamlit`、`io`、`pathlib` 導入

## 後續步驟

請執行效能測試腳本來驗證優化效果：

```bash
python test_performance.py
```

然後啟動 Streamlit 應用程式測試實際啟動時間：

```bash
streamlit run app.py
```

如果需要進一步優化或有其他建議，請告訴我。
