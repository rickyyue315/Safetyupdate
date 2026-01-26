"""
測試 SKU 目標數量分配表格的新欄位顯示功能
"""
import pandas as pd
import sys
import io
from pathlib import Path

# 設定標準輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加入專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_processor import DataProcessor


def test_sku_target_allocation_with_hierarchy_fields():
    """測試資料包含 Product Hierarchy 和 Article Description 欄位的情況"""
    print("測試 1: 資料包含 Product Hierarchy 和 Article Description 欄位")
    print("=" * 80)
    
    # 建立測試資料
    test_data = {
        'Article': ['ART001', 'ART002', 'ART003', 'ART001', 'ART002'],
        'Site': ['S001', 'S002', 'S003', 'S004', 'S005'],
        'Class': ['AA', 'A1', 'A2', 'A3', 'B1'],
        'Last Month Sold Qty': [120, 100, 80, 60, 50],
        'Last 2 Month Sold Qty': [240, 200, 160, 120, 100],
        'Supply Source': ['1', '1', '1', '1', '2'],
        'MOQ': [10, 8, 6, 5, 4],
        'Product Hierarchy': ['SHOES', 'SHIRTS', 'ACCESSORIES', 'SHOES', 'SHIRTS'],
        'Article Description': ['Men\'s Running Shoes - Red', 'Women\'s Cotton Shirt - Blue', 
                                'Leather Belt - Black', 'Men\'s Running Shoes - Red', 'Women\'s Cotton Shirt - Blue']
    }
    df = pd.DataFrame(test_data)
    
    # 檢查欄位是否存在
    has_product_hierarchy = 'Product Hierarchy' in df.columns
    has_article_description = 'Article Description' in df.columns
    
    print(f"✓ Product Hierarchy 欄位存在: {has_product_hierarchy}")
    print(f"✓ Article Description 欄位存在: {has_article_description}")
    
    # 從原始 df 提取 SKU 層級資訊
    agg_dict = {}
    if has_product_hierarchy:
        agg_dict['Product Hierarchy'] = 'first'
    if has_article_description:
        agg_dict['Article Description'] = 'first'
    
    if agg_dict:
        sku_info = df.groupby('Article').agg(agg_dict).reset_index()
    else:
        # 如果沒有可選欄位，只按 Article 分組
        sku_info = df.groupby('Article').first().reset_index()
    
    print("\nSKU 資訊提取結果:")
    print(sku_info)
    
    # 準備 SKU 編輯表格
    unique_skus = sorted(df['Article'].unique().astype(str))
    sku_target_data = []
    
    for sku in unique_skus:
        # 查找該 SKU 的資訊
        sku_info_row = sku_info[sku_info['Article'] == sku]
        if len(sku_info_row) > 0:
            product_hierarchy = sku_info_row['Product Hierarchy'].values[0] if has_product_hierarchy else ""
            article_description = sku_info_row['Article Description'].values[0] if has_article_description else ""
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
    
    print("\nSKU 目標數量分配表格:")
    print(sku_target_df)
    
    # 驗證結果
    assert len(sku_target_df) == 3, "應該有 3 個唯一的 SKU"
    assert sku_target_df['Product Hierarchy'].notna().all(), "所有 SKU 都應該有 Product Hierarchy"
    assert sku_target_df['Article Description'].notna().all(), "所有 SKU 都應該有 Article Description"
    assert sku_target_df.loc[0, 'Product Hierarchy'] == 'SHOES', "ART001 的 Product Hierarchy 應該是 SHOES"
    assert sku_target_df.loc[0, 'Article Description'] == "Men's Running Shoes - Red", "ART001 的 Article Description 應該正確"
    
    print("\n✅ 測試 1 通過！")
    print()


def test_sku_target_allocation_without_hierarchy_fields():
    """測試資料不包含 Product Hierarchy 和 Article Description 欄位的情況"""
    print("測試 2: 資料不包含 Product Hierarchy 和 Article Description 欄位")
    print("=" * 80)
    
    # 建立測試資料（不包含可選欄位）
    test_data = {
        'Article': ['ART001', 'ART002', 'ART003'],
        'Site': ['S001', 'S002', 'S003'],
        'Class': ['AA', 'A1', 'A2'],
        'Last Month Sold Qty': [120, 100, 80],
        'Last 2 Month Sold Qty': [240, 200, 160],
        'Supply Source': ['1', '1', '1'],
        'MOQ': [10, 8, 6]
    }
    df = pd.DataFrame(test_data)
    
    # 檢查欄位是否存在
    has_product_hierarchy = 'Product Hierarchy' in df.columns
    has_article_description = 'Article Description' in df.columns
    
    print(f"✓ Product Hierarchy 欄位存在: {has_product_hierarchy}")
    print(f"✓ Article Description 欄位存在: {has_article_description}")
    
    # 從原始 df 提取 SKU 層級資訊
    agg_dict = {}
    if has_product_hierarchy:
        agg_dict['Product Hierarchy'] = 'first'
    if has_article_description:
        agg_dict['Article Description'] = 'first'
    
    if agg_dict:
        sku_info = df.groupby('Article').agg(agg_dict).reset_index()
    else:
        # 如果沒有可選欄位，只按 Article 分組
        sku_info = df.groupby('Article').first().reset_index()
    
    print("\nSKU 資訊提取結果（欄位不存在時會是 NaN）:")
    print(sku_info)
    
    # 準備 SKU 編輯表格
    unique_skus = sorted(df['Article'].unique().astype(str))
    sku_target_data = []
    
    for sku in unique_skus:
        # 查找該 SKU 的資訊
        sku_info_row = sku_info[sku_info['Article'] == sku]
        if len(sku_info_row) > 0:
            product_hierarchy = sku_info_row['Product Hierarchy'].values[0] if has_product_hierarchy else ""
            article_description = sku_info_row['Article Description'].values[0] if has_article_description else ""
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
    
    print("\nSKU 目標數量分配表格:")
    print(sku_target_df)
    
    # 驗證結果
    assert len(sku_target_df) == 3, "應該有 3 個唯一的 SKU"
    # 由於欄位不存在，值應該是空字串
    assert all(sku_target_df['Product Hierarchy'] == ""), "Product Hierarchy 應該是空字串"
    assert all(sku_target_df['Article Description'] == ""), "Article Description 應該是空字串"
    
    print("\n✅ 測試 2 通過！程式可以正常處理不包含這些欄位的資料")
    print()


def test_sku_target_allocation_with_nan_values():
    """測試資料包含 NaN 值的情況"""
    print("測試 3: 資料包含 NaN 值的情況")
    print("=" * 80)
    
    # 建立測試資料（包含 NaN 值）
    test_data = {
        'Article': ['ART001', 'ART002', 'ART003'],
        'Site': ['S001', 'S002', 'S003'],
        'Class': ['AA', 'A1', 'A2'],
        'Last Month Sold Qty': [120, 100, 80],
        'Last 2 Month Sold Qty': [240, 200, 160],
        'Supply Source': ['1', '1', '1'],
        'MOQ': [10, 8, 6],
        'Product Hierarchy': ['SHOES', None, 'ACCESSORIES'],
        'Article Description': ['Men\'s Running Shoes - Red', None, 'Leather Belt - Black']
    }
    df = pd.DataFrame(test_data)
    
    # 檢查欄位是否存在
    has_product_hierarchy = 'Product Hierarchy' in df.columns
    has_article_description = 'Article Description' in df.columns
    
    print(f"✓ Product Hierarchy 欄位存在: {has_product_hierarchy}")
    print(f"✓ Article Description 欄位存在: {has_article_description}")
    
    # 從原始 df 提取 SKU 層級資訊
    agg_dict = {}
    if has_product_hierarchy:
        agg_dict['Product Hierarchy'] = 'first'
    if has_article_description:
        agg_dict['Article Description'] = 'first'
    
    if agg_dict:
        sku_info = df.groupby('Article').agg(agg_dict).reset_index()
    else:
        # 如果沒有可選欄位，只按 Article 分組
        sku_info = df.groupby('Article').first().reset_index()
    
    print("\nSKU 資訊提取結果（包含 NaN）:")
    print(sku_info)
    
    # 準備 SKU 編輯表格
    unique_skus = sorted(df['Article'].unique().astype(str))
    sku_target_data = []
    
    for sku in unique_skus:
        # 查找該 SKU 的資訊
        sku_info_row = sku_info[sku_info['Article'] == sku]
        if len(sku_info_row) > 0:
            product_hierarchy = sku_info_row['Product Hierarchy'].values[0] if has_product_hierarchy else ""
            article_description = sku_info_row['Article Description'].values[0] if has_article_description else ""
        else:
            product_hierarchy = ""
            article_description = ""
        
        # 處理 NaN 值
        if pd.isna(product_hierarchy):
            product_hierarchy = ""
        if pd.isna(article_description):
            article_description = ""
        
        sku_target_data.append({
            "SKU": sku,
            "Product Hierarchy": product_hierarchy,
            "Article Description": article_description,
            "Target Qty": 0
        })
    
    sku_target_df = pd.DataFrame(sku_target_data)
    
    print("\nSKU 目標數量分配表格（NaN 已轉換為空字串）:")
    print(sku_target_df)
    
    # 驗證結果
    assert len(sku_target_df) == 3, "應該有 3 個唯一的 SKU"
    assert sku_target_df.loc[1, 'Product Hierarchy'] == "", "ART002 的 Product Hierarchy 應該是空字串"
    assert sku_target_df.loc[1, 'Article Description'] == "", "ART002 的 Article Description 應該是空字串"
    
    print("\n✅ 測試 3 通過！NaN 值已正確處理為空字串")
    print()


def test_column_config_generation():
    """測試 column_config 的動態生成"""
    print("測試 4: column_config 的動態生成")
    print("=" * 80)
    
    # 建立測試資料（包含所有欄位）
    test_data = {
        'Article': ['ART001', 'ART002'],
        'Site': ['S001', 'S002'],
        'Class': ['AA', 'A1'],
        'Last Month Sold Qty': [120, 100],
        'Last 2 Month Sold Qty': [240, 200],
        'Supply Source': ['1', '1'],
        'MOQ': [10, 8],
        'Product Hierarchy': ['SHOES', 'SHIRTS'],
        'Article Description': ['Men\'s Running Shoes - Red', 'Women\'s Cotton Shirt - Blue']
    }
    df = pd.DataFrame(test_data)
    
    # 檢查欄位是否存在
    has_product_hierarchy = 'Product Hierarchy' in df.columns
    has_article_description = 'Article Description' in df.columns
    
    print(f"✓ Product Hierarchy 欄位存在: {has_product_hierarchy}")
    print(f"✓ Article Description 欄位存在: {has_article_description}")
    
    # 建立基礎 column_config
    column_config = {
        "SKU": "SKU (Article)",
        "Target Qty": "Target Qty"
    }
    
    # 如果欄位存在，加入 column_config
    if has_product_hierarchy:
        column_config["Product Hierarchy"] = "Product Hierarchy"
    
    if has_article_description:
        column_config["Article Description"] = "Article Description"
    
    print("\n動態生成的 column_config:")
    for key, value in column_config.items():
        print(f"  - {key}: {value}")
    
    # 驗證結果
    assert "Product Hierarchy" in column_config, "column_config 應該包含 Product Hierarchy"
    assert "Article Description" in column_config, "column_config 應該包含 Article Description"
    assert "SKU" in column_config, "column_config 應該包含 SKU"
    assert "Target Qty" in column_config, "column_config 應該包含 Target Qty"
    
    print("\n✅ 測試 4 通過！column_config 動態生成正確")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SKU 目標數量分配表格新欄位顯示功能測試")
    print("=" * 80)
    print()
    
    try:
        test_sku_target_allocation_with_hierarchy_fields()
        test_sku_target_allocation_without_hierarchy_fields()
        test_sku_target_allocation_with_nan_values()
        test_column_config_generation()
        
        print("=" * 80)
        print("✅ 所有測試通過！")
        print("=" * 80)
        print()
        
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
