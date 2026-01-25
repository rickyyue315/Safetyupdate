# 新增 Reset 功能鍵實作計畫

## 概述
在側邊欄的自定資料欄中新增一個 "Reset" 功能鍵，讓使用者可以重置所有欄位的設定，回到預設值。

## 預設值定義

根據 [`config/settings.py`](config/settings.py:12-31) 中的 [`Settings`](config/settings.py:9) 類別，預設值如下：

| 設定項目 | 預設值 |
|---------|-------|
| `max_safety_stock_days` | 7 |
| `moq_multiplier` | 1.25 |
| `moq_constraint_mode` | "multiplier" |
| `shop_class_max_days` | {} (空字典) |

## 實作步驟

### 步驟 1: 修改 [`display_settings_panel`](app.py:94-174) 函數

在 [`app.py`](app.py:1) 的 [`display_settings_panel`](app.py:94) 函數中，在「儲存設定」按鈕旁邊新增一個「Reset」按鈕。

#### 位置
將 Reset 按鈕放在「儲存設定」按鈕的同一行或下一行，方便使用者操作。

#### 按鈕設計
```python
# Reset 按鈕
if st.sidebar.button("🔄 重置設定"):
    # 建立預設設定
    default_settings = Settings()
    # 儲存預設設定
    save_settings(default_settings)
    # 顯示成功訊息
    st.sidebar.success("設定已重置為預設值！")
    # 使用 st.rerun() 重新載入頁面以更新 UI
    st.rerun()
```

### 步驟 2: 確認重置邏輯

當使用者點擊「Reset」按鈕時，需要執行以下操作：

1. **建立預設設定實例**：呼叫 [`Settings()`](config/settings.py:12) 不帶任何參數的建構函式
2. **儲存到檔案**：使用 [`save_settings()`](app.py:36-44) 函數將預設設定儲存到 `config/settings.json`
3. **顯示成功訊息**：使用 [`st.sidebar.success()`](app.py:172) 顯示確認訊息
4. **重新載入頁面**：使用 [`st.rerun()`](app.py) 重新載入 Streamlit 應用程式，讓 UI 顯示更新後的預設值

### 步驟 3: UI 佈局建議

建議將兩個按鈕並排顯示，方便使用者操作：

```python
# 按鈕區域
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.sidebar.button("🔄 重置設定"):
        # Reset 邏輯
with col2:
    if st.sidebar.button("💾 儲存設定"):
        # Save 邏輯
```

或者垂直排列：

```python
# Reset 按鈕
if st.sidebar.button("🔄 重置設定"):
    # Reset 邏輯

# 儲存設定按鈕
if st.sidebar.button("💾 儲存設定"):
    # Save 邏輯
```

## 涉及的檔案

- [`app.py`](app.py:1) - 主要應用程式檔案，需要修改 [`display_settings_panel`](app.py:94) 函數
- [`config/settings.py`](config/settings.py:1) - 設定類別定義（不需要修改）

## 測試計畫

完成實作後，需要測試以下情境：

1. **基本重置功能**：
   - 修改一些設定值
   - 點擊「Reset」按鈕
   - 確認所有設定恢復到預設值

2. **自訂 Shop Class 天數上限重置**：
   - 啟用自訂 Shop Class 天數上限
   - 設定一些自訂值
   - 點擊「Reset」按鈮
   - 確認自訂設定被清除，回到使用全域設定

3. **設定檔案更新**：
   - 點擊「Reset」後
   - 檢查 `config/settings.json` 檔案內容是否正確更新為預設值

4. **UI 更新**：
   - 確認重置後，UI 上的所有欄位都顯示正確的預設值

## 預期結果

完成後，使用者可以：
- 在側邊欄看到一個「🔄 重置設定」按鈕
- 點擊後，所有設定立即恢復到預設值
- 設定檔案被更新為預設值
- UI 顯示更新後的預設值
