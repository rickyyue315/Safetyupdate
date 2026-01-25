# SKU Target Allocation Feature Implementation

## 需求概述

新增功能以支援使用者在網頁介面輸入 SKU 層級的 Target Qty，並將其按比例分配至各店鋪的 Safety Stock。

### 核心需求
1. **輸入方式**：在網頁介面（計算頁面）直接輸入每個 SKU 的 Target Qty。
2. **分配邏輯**：
   - 首先執行標準的 Safety Stock 計算。
   - 計算該 SKU 在所有店鋪的標準 Safety Stock 總和 (`Total_Standard_SS`)。
   - 將使用者的 `SKU_Target_Qty` 按比例分配：
     `New_SS = (Standard_SS / Total_Standard_SS) * SKU_Target_Qty`
3. **優先順序**：Allocation 邏輯在標準計算之後執行，會覆蓋標準計算結果。

## 實施步驟

### 1. 更新 app.py UI
- 在檔案上傳後、計算按鈕前，新增 "SKU Target Qty Allocation" 區域。
- 使用 `st.data_editor` 顯示所有 SKU 列表，供使用者輸入 Target Qty。
- 收集使用者輸入的 `sku_targets` 字典。

### 2. 更新 app.py 計算邏輯
- 修改 `calculate_safety_stock` 函數，接收 `sku_targets` 參數。
- 執行標準計算流程，取得 `results_df`。
- 執行分配邏輯：
  - 遍歷有設定 Target Qty 的 SKU。
  - 計算該 SKU 的總標準 SS。
  - 計算分配係數 (`Factor = Target / Total`)。
  - 更新每個店鋪的 `Suggested_Safety_Stock`。
  - 處理整數分配後的餘數（分配給小數部分最大的店鋪）。
  - 更新 `Safety_Stock_Days` 和 `Notes`。
  - 設定 `Constraint_Applied` 為 `'Target Allocation'`。
  - 設定 `Calculation_Mode` 為 `'Allocation'`。

## 計算細節

### 分配公式
$$
Allocated\_SS_i = \lfloor Standard\_SS_i \times \frac{Target\_Qty}{\sum Standard\_SS} \rfloor
$$

### 餘數處理
$$
Remainder = Target\_Qty - \sum Allocated\_SS_i
$$
餘數將分配給 $(Standard\_SS_i \times Factor) - Allocated\_SS_i$ 最大（即小數部分最大）的前 $N$ 個店鋪。

## 欄位變更
- **Constraint_Applied**: 當觸發分配時，值為 `'Target Allocation'`。
- **Calculation_Mode**: 當觸發分配時，值為 `'Allocation'`。
- **Notes**: 新增分配詳情（Target Qty, Factor, Allocated SS）。
