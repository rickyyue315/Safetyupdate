# 安全庫存計算邏輯修改計畫

## 1. 核心計算邏輯修改
檔案：[`core/calculator.py`](core/calculator.py)

將 `apply_max_days_constraint` 函數中的 `min` 改為 `max`。

```python
# 修改前
suggested_ss = min(ss_after_moq, max_allowed_ss)
max_days_constraint_applied = suggested_ss < ss_after_moq

# 修改後
suggested_ss = max(ss_after_moq, max_allowed_ss)
max_days_constraint_applied = suggested_ss > ss_after_moq
```

## 2. 系統設定修改
檔案：[`config/settings.py`](config/settings.py)

- 將 `max_safety_stock_days` 預設值從 14 改為 7。
- 將驗證範圍從 7-14 改為 3-21。

## 3. Web UI 修改
檔案：[`app.py`](app.py)

- `display_home_page`: 更新公式說明。
- `display_settings_panel`: 
    - 將 `st.sidebar.slider` 的 `min_value` 改為 3，`max_value` 改為 21。
    - 更新 `help` 說明文字。
    - 將 `st.sidebar.number_input` (Shop Class 設定) 的範圍也同步調整為 3-21。

## 4. 驗證計畫
- 啟動 Streamlit 應用程式。
- 檢查側邊欄的預設值是否為 7。
- 檢查 slider 是否可以調整至 3 到 21 之間。
- 上傳測試資料，驗證 `Suggested_Safety_Stock` 是否正確套用了 `max(SS_after_MOQ, Avg_Daily_Sales × Max_Days)`。
