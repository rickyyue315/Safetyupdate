# SKU 目標數量分配表格新增欄位實作計畫

## 需求概述

在網頁的「SKU 目標數量分配 (Target Safety Stock)」表格中新增兩個欄位，方便使用者查找 SKU：
1. **Product Hierarchy** (產品階層)
2. **Article Description** (商品描述)

## 現狀分析

### 目前實作 (app.py 第 669-702 行)
```python
# SKU Target Qty Allocation Section
st.subheader("🎯 SKU 目標數量分配 (Target Safety Stock)")
st.info("在此輸入 SKU 的總目標數量，系統將自動按比例分配至各店舖。若輸入 0 則使用標準計算公式。")

# 準備 SKU 編輯表格
unique_skus = sorted(df['Article'].unique().astype(str))
sku_target_data = [{"SKU": sku, "Target Qty": 0} for sku in unique_skus]
sku_target_df = pd.DataFrame(sku_target_data)

# 顯示編輯器
edited_sku_df = st.data_editor(
    sku_target_df,
    column_config={
        "SKU": st.column_config.TextColumn("SKU (Article)", disabled=True),
        "Target Qty": st.column_config.NumberColumn(
            "Target Qty",
            min_value=0,
            step=1,
            format="%d",
            help="輸入該 SKU 的總目標數量"
        )
    },
    use_container_width=True,
    hide_index=True,
    key="sku_target_editor"
)
```

### 資料來源
- 原始資料 `df` 已包含以下欄位（可選欄位）：
  - `Article` (SKU)
  - `Product Hierarchy`
  - `Article Description`
  - 其他欄位...

### 技術考量
1. **一對多關係**：一個 SKU 可能對應多筆記錄（不同店舖）
2. **資料一致性**：同一 SKU 的 Product Hierarchy 和 Article Description 應該相同
3. **欄位可選性**：Product Hierarchy 和 Article Description 是可選欄位，可能不存在於某些資料集中

## 實作計畫

### 步驟 1: 從原始 df 提取 SKU 層級資訊

在準備 `sku_target_df` 之前，先從原始 `df` 中提取每個 SKU 對應的 Product Hierarchy 和 Article Description：

```python
# 從原始 df 提取 SKU 層級資訊
sku_info = df.groupby('Article').agg({
    'Product Hierarchy': 'first',
    'Article Description': 'first'
}).reset_index()

# 準備 SKU 編輯表格
unique_skus = sorted(df['Article'].unique().astype(str))
sku_target_data = []

for sku in unique_skus:
    # 查找該 SKU 的資訊
    sku_info_row = sku_info[sku_info['Article'] == sku]
    if len(sku_info_row) > 0:
        product_hierarchy = sku_info_row['Product Hierarchy'].values[0]
        article_description = sku_info_row['Article Description'].values[0]
    else:
        product_hierarchy = ""
        article_description = ""

    sku_target_data.append({
        "SKU": sku,
        "Product Hierarchy": product_hierarchy,
        "Article Description": article_description,
        "Target Qty": 0
    })

sku_target_df = pd.DataFrame(sku_target_data)
```

### 步驟 2: 更新 st.data_editor 的 column_config

新增 Product Hierarchy 和 Article Description 欄位的配置：

```python
edited_sku_df = st.data_editor(
    sku_target_df,
    column_config={
        "SKU": st.column_config.TextColumn("SKU (Article)", disabled=True),
        "Product Hierarchy": st.column_config.TextColumn(
            "Product Hierarchy",
            disabled=True,
            help="產品階層"
        ),
        "Article Description": st.column_config.TextColumn(
            "Article Description",
            disabled=True,
            width="large",
            help="商品描述"
        ),
        "Target Qty": st.column_config.NumberColumn(
            "Target Qty",
            min_value=0,
            step=1,
            format="%d",
            help="輸入該 SKU 的總目標數量"
        )
    },
    use_container_width=True,
    hide_index=True,
    key="sku_target_editor"
)
```

### 步驟 3: 處理可選欄位

由於 Product Hierarchy 和 Article Description 是可選欄位，需要處理欄位不存在的情況：

```python
# 檢查欄位是否存在
has_product_hierarchy = 'Product Hierarchy' in df.columns
has_article_description = 'Article Description' in df.columns

# 準備 SKU 編輯表格
unique_skus = sorted(df['Article'].unique().astype(str))
sku_target_data = []

for sku in unique_skus:
    # 查找該 SKU 的第一筆記錄
    sku_records = df[df['Article'] == sku]
    first_record = sku_records.iloc[0]

    # 提取資訊（如果欄位存在）
    product_hierarchy = first_record['Product Hierarchy'] if has_product_hierarchy else ""
    article_description = first_record['Article Description'] if has_article_description else ""

    sku_target_data.append({
        "SKU": sku,
        "Product Hierarchy": product_hierarchy,
        "Article Description": article_description,
        "Target Qty": 0
    })

sku_target_df = pd.DataFrame(sku_target_data)
```

### 步驟 4: 條件性顯示欄位

根據欄位是否存在，動態調整 column_config：

```python
# 建立基礎 column_config
column_config = {
    "SKU": st.column_config.TextColumn("SKU (Article)", disabled=True),
    "Target Qty": st.column_config.NumberColumn(
        "Target Qty",
        min_value=0,
        step=1,
        format="%d",
        help="輸入該 SKU 的總目標數量"
    )
}

# 如果欄位存在，加入 column_config
if has_product_hierarchy:
    column_config["Product Hierarchy"] = st.column_config.TextColumn(
        "Product Hierarchy",
        disabled=True,
        help="產品階層"
    )

if has_article_description:
    column_config["Article Description"] = st.column_config.TextColumn(
        "Article Description",
        disabled=True,
        width="large",
        help="商品描述"
    )

edited_sku_df = st.data_editor(
    sku_target_df,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    key="sku_target_editor"
)
```

## 欄位顯示順序

建議的欄位顯示順序：
1. **SKU** (Article) - 唯讀
2. **Product Hierarchy** - 唯讀
3. **Article Description** - 唯讀
4. **Target Qty** - 可編輯

## 預期效果

### 修改前
| SKU (Article) | Target Qty |
|---------------|------------|
| 1001 | 0 |
| 1002 | 0 |
| 1003 | 0 |

### 修改後
| SKU (Article) | Product Hierarchy | Article Description | Target Qty |
|---------------|-------------------|---------------------|------------|
| 1001 | SHOES | Men's Running Shoes | 0 |
| 1002 | SHIRTS | Women's Cotton Shirt | 0 |
| 1003 | ACCESSORIES | Leather Belt | 0 |

## 注意事項

1. **資料一致性**：假設同一 SKU 的 Product Hierarchy 和 Article Description 在所有記錄中相同
2. **欄位可選性**：如果資料集中不包含這些欄位，表格仍應正常運作
3. **效能考量**：使用 `groupby` 和 `first()` 方法確保效能
4. **使用者體驗**：新欄位設為 disabled，避免使用者誤編輯

## 測試計畫

1. **正常情況**：資料包含 Product Hierarchy 和 Article Description 欄位
2. **缺少欄位**：資料不包含這些欄位，確保程式不會報錯
3. **多筆記錄**：同一 SKU 有多筆記錄，確認使用第一筆記錄的值
4. **空值處理**：欄位值為空或 NaN 的處理

## 實作位置

- **檔案**: `app.py`
- **函數**: `main()` 函數中的「SKU Target Qty Allocation Section」區塊
- **行數**: 第 669-702 行
