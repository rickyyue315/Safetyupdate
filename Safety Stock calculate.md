- **系統名稱**  
  Safety(Buffer) Stock Calculation v2.0  
  安全(緩衝)庫存計算機

- **系統目的**  
  - 根據實際可用資料欄位及商業限制，計算合理的安全庫存建議值  
  - 確保重點店（高階 Shop Class）擁有較高服務水準  
  - 滿足 MOQ 最小訂購量要求  
  - 允許使用者自訂安全庫存天數上限（7–14 天）
  - **新增**：支援 Target Qty 模式，可按未來一個月的銷售預測直接設定 Safety Stock

- **核心計算公式**  
  - 初步安全庫存 SS_preliminary = Avg_Daily_Sales × √Lead_Time_Days × MF  
  - Avg_Daily_Sales = (Last Month Sold Qty + Last 2 Month Sold Qty) / 60  
  - Lead_Time_Days：依 Supply Source 判斷  
    - "1" 或 "4" → 7 天（行貨）  
    - "2" → 3 天（倉貨）  
    - 其他 → 預設 7 天  
  - MF（合併因素）：依 Shop Class 固定查表

- **合併因素 MF 對照表**  
  - AA → 2.58 (99.5%)  
  - A1 → 2.33 (99.0%)  
  - A2 → 2.05 (98.0%)  
  - A3 → 1.88 (97.0%)  
  - B1 → 1.75 (96.0%)  
  - B2 → 1.645 (95.0%)  
  - C1 → 1.555 (94.0%)  
  - C2 → 1.48 (93.0%)  
  - D1 → 1.28 (90.0%)

- **最終安全庫存調整規則（優先順序）**
  1. **Target Safety Stock 模式**（如果在 UI 輸入了 SKU Target Qty）：
     - 根據輸入的 SKU 總目標數量，按標準模式計算出的比例分配至各店舖
     - Target_Safety_Stock = (SKU_Total_Target / SKU_Current_Total_SS) × Store_Suggested_SS
     - 標記為 `Target Safety Stock` 模式
  2. **Target Qty 模式**（如果啟用且 Target Qty 存在）：
     - 直接使用 Target Qty 作為 Safety Stock
     - 跳過原有的 MF、MOQ 約束、天數上限計算
     - Safety Stock Days = Target Qty / Avg_Daily_Sales
  3. **標準模式**（如果 Target Qty 不存在或未啟用 Target Qty 模式）：
     - 計算初步值：SS_preliminary = Avg_Daily_Sales × √Lead_Time_Days × MF
     - 套用 MOQ 約束（最高優先）：
       - Suggested_SS = max(SS_preliminary, MOQ × 1.25)
       - 預設乘數 1.25，可後台切換為 MOQ + 1 模式
     - 套用使用者設定的天數上限：
       - Max_Allowed_SS = Avg_Daily_Sales × User_Defined_Max_Days
       - Suggested_Safety_Stock = min(SS_after_MOQ, Max_Allowed_SS)
     - 使用者可設定天數上限：
       - 預設：14 天
       - 允許範圍：7–14 天（整數）
       - 設定位置：網頁 UI 全域或按 Shop Class 設定

- **建議輸入資料欄位**  
  - Article（商品編號）  
  - Site（門市代碼）  
  - Class（店舖等級：AA / A1 / A2 / A3 / B1 / B2 / C1 / C2 / D1）  
  - Last Month Sold Qty（上個月銷量）  
  - Last 2 Month Sold Qty（前兩個月銷量總和）  
  - Supply Source（供應來源："1"、"2"、"4"等）  
  - MOQ（最小訂購量，件）  
  - **Target Qty**（目標數量，可選）- 未來一個月的預測 Safety Stock

- **輸出核心欄位**  
  - Article / Site / Class  
  - Avg_Daily_Sales  
  - Lead_Time_Days  
  - MF_Used  
  - Preliminary_SS  
  - SS_after_MOQ  
  - User_Max_Days_Applied  
  - Suggested_Safety_Stock（最終建議值）  
  - Constraint_Applied（MOQ / 天數上限 / 兩者 / Target Qty / Target Safety Stock）  
  - Safety_Stock_Days（最終值可支撐天數）  
  - **Target_Qty_Used**（是否使用了 Target Qty：True/False）  
  - **Calculation_Mode**（計算模式："Target Qty"、"Standard" 或 "Target Safety Stock"）

- **網頁 UI 使用者設定項目**
  - 安全庫存天數上限（預設 14 天，範圍 7–14 天）
  - MOQ 約束乘數（預設 1.25，可調整）
  - MOQ 約束模式（乘數模式 / 加 1 模式）
  - **Target Qty 模式**（預設關閉）
    - 啟用後，如果輸入資料包含 Target Qty 欄位，直接使用 Target Qty 作為 Safety Stock
    - 跳過原有的 MF、MOQ 約束、天數上限計算
    - 適合用於按未來一個月的銷售預測來設定 Safety Stock
  - **Target Safety Stock 模式**（新增）
    - 在計算頁面輸入 SKU 的總目標數量
    - 系統自動按標準模式計算出的比例分配至各店舖

- **實作注意事項**  
  - Avg_Daily_Sales 建議保留 2 位小數  
  - 觸發 MOQ 或天數上限時，於結果表格標示原因  
  - 使用者天數上限應於每次計算前讀取並記錄  
  - 未來可擴展：按商品類別或 Shop Class 設定不同上限

- **後續迭代方向**  
  - 引入銷量標準差計算，升級為完整統計模型  
  - 加入季節性 / 促銷調整係數  
  - 結合現有庫存與在途量，產出建議訂貨量  
  - 支援多層級天數上限設定