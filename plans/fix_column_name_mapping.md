# 欄位名稱映射修正計劃

## 問題分析

### 發現的問題

上傳檔案時網頁顯示資料檔案缺少必要欄位：
- `Last 2 Month Sold Qty`
- `Supply Source`

### 根本原因

檢查實際上傳的檔案後，發現欄位名稱不匹配：

1. **Supply Source 大小寫問題**
   - 實際檔案：`Supply source`（小寫 s）
   - 系統期望：`Supply Source`（大寫 S）

2. **Last 2 Month Sold Qty 欄位名稱不完整**
   - 實際檔案：`Last 2 Month`（缺少 "Sold Qty"）
   - 系統期望：`Last 2 Month Sold Qty`

## 解決方案

### 架構設計

在資料載入流程中添加欄位名稱標準化層：

```mermaid
graph TD
    A[用戶上傳檔案] --> B[DataProcessor.load_data]
    B --> C[pandas 讀取檔案]
    C --> D[欄位名稱標準化]
    D --> E[驗證必要欄位]
    E --> F{驗證通過?}
    F -->|是| G[返回標準化後的 DataFrame]
    F -->|否| H[返回錯誤訊息]
```

### 實作步驟

#### 步驟 1：在 core/constants.py 中定義欄位名稱映射字典

新增一個 `COLUMN_NAME_ALIASES` 字典，用於將常見的欄位名稱變體映射到標準名稱：

```python
# 欄位名稱映射表（用於處理不同的欄位名稱變體）
COLUMN_NAME_ALIASES: Dict[str, str] = {
    # Supply Source 的變體
    "Supply source": FIELD_SUPPLY_SOURCE,
    "supply source": FIELD_SUPPLY_SOURCE,
    "supply Source": FIELD_SUPPLY_SOURCE,
    
    # Last 2 Month Sold Qty 的變體
    "Last 2 Month": FIELD_LAST_2_MONTH_SOLD_QTY,
    "last 2 month": FIELD_LAST_2_MONTH_SOLD_QTY,
    "Last 2 month": FIELD_LAST_2_MONTH_SOLD_QTY,
    "last 2 Month": FIELD_LAST_2_MONTH_SOLD_QTY,
    
    # 其他可能的變體（預留擴展空間）
    # "Last Month Sold Qty": FIELD_LAST_MONTH_SOLD_QTY,
    # "Last month sold qty": FIELD_LAST_MONTH_SOLD_QTY,
    # ...
}
```

#### 步驟 2：在 core/data_processor.py 中添加欄位名稱標準化方法

新增一個靜態方法 `normalize_column_names`，用於將 DataFrame 的欄位名稱標準化：

```python
@staticmethod
def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    標準化欄位名稱
    
    將常見的欄位名稱變體映射到標準名稱
    
    參數:
        df: 原始 DataFrame
        
    返回:
        欄位名稱標準化後的 DataFrame
    """
    from core.constants import COLUMN_NAME_ALIASES
    
    # 建立副本以避免修改原始資料
    df_normalized = df.copy()
    
    # 建立欄位名稱映射
    column_mapping = {}
    for col in df_normalized.columns:
        # 檢查是否為別名
        if col in COLUMN_NAME_ALIASES:
            column_mapping[col] = COLUMN_NAME_ALIASES[col]
        # 檢查是否為大小寫變體（忽略大小寫比較）
        elif col.lower() in [k.lower() for k in COLUMN_NAME_ALIASES.keys()]:
            # 找到對應的標準名稱
            for alias, standard in COLUMN_NAME_ALIASES.items():
                if col.lower() == alias.lower():
                    column_mapping[col] = standard
                    break
    
    # 應用欄位名稱映射
    if column_mapping:
        df_normalized = df_normalized.rename(columns=column_mapping)
    
    return df_normalized
```

#### 步驟 3：更新 load_data 方法以自動應用欄位名稱映射

修改 `load_data` 方法，在載入資料後自動應用欄位名稱標準化：

```python
@staticmethod
def load_data(file_path: str) -> pd.DataFrame:
    """
    載入 CSV 或 Excel 檔案
    
    自動偵測檔案格式並使用適當的 pandas 方法載入，
    並自動標準化欄位名稱
    
    參數:
        file_path: 檔案路徑
        
    返回:
        包含資料的 DataFrame（欄位名稱已標準化）
        
    異常:
        ValueError: 當檔案格式不支援時
        FileNotFoundError: 當檔案不存在時
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"檔案不存在：{file_path}")
    
    file_ext = path.suffix.lower()
    
    if file_ext == '.csv':
        df = pd.read_csv(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(
            f"不支援的檔案格式：{file_ext}，"
            f"請使用 .csv、.xlsx 或 .xls 格式"
        )
    
    # 自動標準化欄位名稱
    df = DataProcessor.normalize_column_names(df)
    
    return df
```

### 預期效果

1. **自動修正大小寫問題**：`Supply source` 會自動映射到 `Supply Source`
2. **自動補全欄位名稱**：`Last 2 Month` 會自動映射到 `Last 2 Month Sold Qty`
3. **向後相容**：現有的正確欄位名稱不受影響
4. **可擴展性**：可以輕鬆添加更多欄位名稱變體

### 測試案例

測試檔案應包含以下欄位名稱變體：

| 標準名稱 | 測試變體 1 | 測試變體 2 |
|---------|-----------|-----------|
| Supply Source | Supply source | supply Source |
| Last 2 Month Sold Qty | Last 2 Month | last 2 month |

### 檔案變更清單

1. `core/constants.py`
   - 新增 `COLUMN_NAME_ALIASES` 字典

2. `core/data_processor.py`
   - 新增 `normalize_column_names` 靜態方法
   - 修改 `load_data` 方法，添加欄位名稱標準化呼叫

### 優勢

- ✅ **使用者友善**：用戶不需要手動修改欄位名稱
- ✅ **自動化**：系統自動處理常見的欄位名稱變體
- ✅ **可維護**：所有映射規則集中在一個地方
- ✅ **可擴展**：可以輕鬆添加新的欄位名稱變體
- ✅ **向後相容**：不影響現有的正確欄位名稱

### 風險評估

| 風險 | 影響 | 緩解措施 |
|-----|------|---------|
| 映射錯誤的欄位名稱 | 低 | 只映射已知的變體，保留原始欄位名稱作為備份 |
| 效能影響 | 低 | 映射操作簡單，對效能影響極小 |
| 未處理的變體 | 中 | 提供清晰的錯誤訊息，告訴用戶缺少哪些欄位 |

## 後續改進建議

1. **添加日誌記錄**：記錄欄位名稱映射的詳細資訊，便於除錯
2. **使用者提示**：當欄位名稱被映射時，顯示提示訊息
3. **擴展映射表**：根據實際使用情況，添加更多常見的欄位名稱變體
4. **驗證工具**：提供一個工具讓用戶預先檢查檔案的欄位名稱是否正確
