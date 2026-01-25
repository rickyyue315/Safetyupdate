# SAP 資料匯出說明新增計劃

## 任務目標
在網頁版面上新增使用說明的提示，指導使用者如何從 SAP 系統匯出資料並準備輸入檔案。

## 顯示位置
- **首頁**（`display_home_page()` 函數）
- 新增一個獨立的「SAP 資料匯出說明」章節
- 使用可折疊設計（`st.expander`）以節省空間

## 設計格式
- 使用 `st.expander()` 創建可折疊區域
- 使用編號列表（1-6）清楚標示步驟
- 使用圖示增強可讀性（如 📋、🔧、💾 等）
- 使用粗體標示關鍵參數（如程式碼、Variant 名稱等）
- 使用分隔線區分不同章節

## 使用說明內容

### SAP 資料匯出步驟

1. **SAP 程式碼**：ZRPMM0015_S
2. **Get Variant**：ACTIVE SHOP
3. **更改 Output Layout**：/SHOP 3M
4. **輸入 SKU**：輸入要查詢的商品編號
5. **轉出成 Excel report**：執行程式並匯出為 Excel 格式
6. **在 Excel 內新增 Class (店舖級別)**：手動新增店舖等級欄位

### 店舖級別說明
店舖級別（Class）可能的值包括：
- AA, A1, A2, A3
- B1, B2
- C1, C2
- D1

## 實作步驟

### 步驟 1：修改 `display_home_page()` 函數
在 `app.py` 的 `display_home_page()` 函數中，新增 SAP 資料匯出說明章節。

位置建議：
- 在「系統簡介」章節之後
- 在「核心功能」章節之前
- 或在「使用說明」章節之前

### 步驟 2：使用 expander 創建可折疊區域
```python
with st.expander("📋 SAP 資料匯出說明", expanded=False):
    st.markdown("""
    ### 從 SAP 系統匯出資料步驟
    
    1. **SAP 程式碼**：`ZRPMM0015_S`
    
    2. **Get Variant**：`ACTIVE SHOP`
    
    3. **更改 Output Layout**：`/SHOP 3M`
    
    4. **輸入 SKU**：輸入要查詢的商品編號
    
    5. **轉出成 Excel report**：執行程式並匯出為 Excel 格式
    
    6. **在 Excel 內新增 Class (店舖級別)**：手動新增店舖等級欄位
    
    ---
    
    ### 店舖級別說明
    
    店舖級別（Class）可能的值包括：
    - AA, A1, A2, A3
    - B1, B2
    - C1, C2
    - D1
    
    > 💡 **提示**：確保 Excel 檔案包含所有必要欄位後再上傳至本系統進行計算。
    """)
```

### 步驟 3：測試顯示效果
- 確認 expander 可以正常展開和折疊
- 確認內容格式正確顯示
- 確認圖示和粗體標示正常運作

## 修改的檔案
- `app.py` - 修改 `display_home_page()` 函數

## 預期效果
使用者可以在首頁看到「📋 SAP 資料匯出說明」的可折疊區域，點擊後可以查看完整的 SAP 資料匯出步驟說明，幫助使用者正確準備輸入資料。
