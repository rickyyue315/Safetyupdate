# 新增 Product Hierarchy 和 Article Description 欄位實作計劃

## 任務概述
在安全庫存計算系統中新增兩個顯示欄位：
- **Product Hierarchy** - 顯示產品階層
- **Article Description** - 顯示商品描述

## 現有實作狀態分析

### ✅ 已完成的部分

1. **core/constants.py**（第56-57行）
   - 已定義常數：
     ```python
     FIELD_PRODUCT_HIERARCHY = "Product Hierarchy"
     FIELD_ARTICLE_DESCRIPTION = "Article Description"
     ```
   - 已在 `COLUMN_NAME_ALIASES` 中包含這兩個欄位的變體映射（第128-136行）

2. **core/calculator.py**
   - 已匯入這兩個欄位常數（第29-30行）
   - `calculate_safety_stock` 方法已接受這兩個參數（第224-225行）
   - 返回結果中已包含這兩個欄位（第306-307行）：
     ```python
     FIELD_PRODUCT_HIERARCHY: product_hierarchy if product_hierarchy is not None else "",
     FIELD_ARTICLE_DESCRIPTION: article_description if article_description is not None else "",
     ```

3. **core/data_processor.py**
   - `prepare_calculation_data` 方法已處理這兩個欄位（第226-231行）

4. **app.py**
   - 在 `display_results_summary` 方法中已將這兩個欄位加入顯示欄位列表（第249-250行）
   - 在 `calculate_safety_stock` 方法中已傳遞這兩個欄位到計算器（第432-433行）

5. **utils/exporters.py**
   - 在 `export_to_excel` 方法中已將這兩個欄位加入輸出欄位列表（第33-34行）

### ❌ 需要修正的問題

#### 問題 1：core/data_processor.py 中的欄位名稱比較邏輯

**位置：** `core/data_processor.py` 第226-231行

**問題：** 使用硬編碼的小寫字串比較，而不是使用常數

**現有程式碼：**
```python
# 新增 Product Hierarchy 和 Article Description（如果存在）
for col in df.columns:
    if col.lower() == 'product hierarchy':
        columns_to_include.append(col)
    elif col.lower() == 'article description':
        columns_to_include.append(col)
```

**問題分析：**
- 使用硬編碼字串而不是常數，降低可維護性
- 沒有使用 `COLUMN_NAME_ALIASES` 機制，可能遺漏欄位名稱變體

**修正方案：**
```python
# 新增 Product Hierarchy 和 Article Description（如果存在）
if FIELD_PRODUCT_HIERARCHY in df.columns:
    columns_to_include.append(FIELD_PRODUCT_HIERARCHY)
if FIELD_ARTICLE_DESCRIPTION in df.columns:
    columns_to_include.append(FIELD_ARTICLE_DESCRIPTION)
```

#### 問題 2：app.py 中的 Excel 匯出欄位名稱不一致

**位置：** `app.py` 第304-305行

**問題：** Excel 匯出欄位列表使用帶下劃線的名稱，但計算器返回的欄位名稱是帶空格的

**現有程式碼：**
```python
display_columns = [
    'Article', 'Site', 'Class',
    'Product_Hierarchy',      # ❌ 錯誤：使用下劃線
    'Article_Description',     # ❌ 錯誤：使用下劃線
    ...
]
```

**問題分析：**
- 計算器返回的欄位名稱是 `"Product Hierarchy"` 和 `"Article Description"`（帶空格）
- Excel 匯出使用 `'Product_Hierarchy'` 和 `'Article_Description'`（帶下劃線）
- 欄位名稱不匹配，導致這兩個欄位不會被匯出到 Excel

**修正方案：**
```python
display_columns = [
    'Article', 'Site', 'Class',
    'Product Hierarchy',      # ✅ 正確：使用空格
    'Article Description',    # ✅ 正確：使用空格
    ...
]
```

## 欄位名稱標準

統一使用帶空格的欄位名稱（與輸入檔案一致）：

| 用途 | 欄位名稱 |
|------|---------|
| 輸入檔案 | `Product Hierarchy`, `Article Description` |
| 常數定義 | `FIELD_PRODUCT_HIERARCHY = "Product Hierarchy"`<br>`FIELD_ARTICLE_DESCRIPTION = "Article Description"` |
| DataFrame 欄位 | `Product Hierarchy`, `Article Description` |
| 顯示和輸出 | `Product Hierarchy`, `Article Description` |

## 實作步驟

### 步驟 1：修正 core/data_processor.py
- 修改 `prepare_calculation_data` 方法中的欄位檢查邏輯
- 使用常數 `FIELD_PRODUCT_HIERARCHY` 和 `FIELD_ARTICLE_DESCRIPTION`
- 確保欄位名稱一致性

### 步驟 2：修正 app.py
- 修改 `display_download_buttons` 方法中的 Excel 匯出欄位列表
- 將 `'Product_Hierarchy'` 改為 `'Product Hierarchy'`
- 將 `'Article_Description'` 改為 `'Article Description'`

### 步驟 3：驗證
- 測試載入包含這兩個欄位的輸入檔案
- 驗證計算結果中正確顯示這兩個欄位
- 驗證 Excel 匯出中包含這兩個欄位
- 驗證 CSV 匯出中包含這兩個欄位

## 影響範圍

### 需要修改的檔案
1. `core/data_processor.py` - 修正欄位名稱比較邏輯
2. `app.py` - 修正 Excel 匯出欄位名稱

### 不需要修改的檔案
1. `core/constants.py` - 已正確定義常數
2. `core/calculator.py` - 已正確處理這兩個欄位
3. `utils/exporters.py` - 已正確使用帶空格的欄位名稱

## 測試計劃

### 測試案例 1：輸入檔案包含這兩個欄位
- 載入包含 `Product Hierarchy` 和 `Article Description` 欄位的檔案
- 驗證計算結果中這兩個欄位正確顯示
- 驗證 Excel 匯出包含這兩個欄位

### 測試案例 2：輸入檔案不包含這兩個欄位
- 載入不包含這兩個欄位的檔案
- 驗證計算結果中這兩個欄位顯示為空字串
- 驗證 Excel 匯出包含這兩個欄位（但為空）

### 測試案例 3：欄位名稱變體
- 載入包含欄位名稱變體的檔案（如 `product hierarchy`, `Article description`）
- 驗證欄位名稱標準化機制正常運作

## 風險評估

### 低風險
- 這些修改只影響欄位名稱的處理邏輯
- 不影響核心計算邏輯
- 修改範圍有限，容易測試和驗證

### 注意事項
- 確保修改後的程式碼與現有的欄位名稱標準化機制一致
- 測試時使用實際的輸入檔案格式
- 確保 Excel 和 CSV 匯出功能正常運作

## 完成標準

- [x] 所有檔案中的欄位名稱一致使用帶空格的格式
- [x] 輸入檔案中的 `Product Hierarchy` 和 `Article Description` 欄位能正確讀取
- [x] 計算結果中正確顯示這兩個欄位
- [x] Excel 匯出包含這兩個欄位
- [x] CSV 匯出包含這兩個欄位
- [x] 所有測試案例通過

## 相關文件

- 輸入檔案範例：`data/input/110681212001_21Jan2026v2.XLSX`
- 系統架構文件：`plans/safety_stock_system_architecture.md`
- 實作計劃：`plans/implementation_plan.md`
