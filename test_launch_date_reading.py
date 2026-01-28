#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Launch Date 讀取和計算功能
"""
import pandas as pd
from datetime import date
from core.data_processor import DataProcessor
from core.calculator import SafetyStockCalculator
from config.settings import Settings

# 讀取測試文件
print("讀取 Test_26Jan2026.XLSX...")
df = pd.read_excel("Test_26Jan2026.XLSX")

print(f"\n檔案包含 {len(df)} 行資料")
print(f"\n欄位列表：")
print(df.columns.tolist())

# 檢查 Launch Date 欄位
if "Launch Date" in df.columns:
    print(f"\n✓ 發現 Launch Date 欄位")
    print(f"\nLaunch Date 資料樣本：")
    print(df["Launch Date"].head(10))
    print(f"\nLaunch Date 資料型別：{df['Launch Date'].dtype}")
    
    # 測試轉換
    print(f"\n轉換首行 Launch Date...")
    first_launch_date = df["Launch Date"].iloc[0]
    print(f"原始值：{first_launch_date}（型別：{type(first_launch_date)}）")
    
    if pd.isna(first_launch_date):
        print("值為 NaN（空值）")
    else:
        # 嘗試轉換為 date
        if hasattr(first_launch_date, 'date'):
            converted = first_launch_date.date()
            print(f"轉換後：{converted}（型別：{type(converted)}）")
        else:
            print(f"無法轉換（無 .date() 方法）")
else:
    print(f"\n✗ 未找到 Launch Date 欄位")

print(f"\n\n第一行資料（用於計算測試）：")
first_row = df.iloc[0]
for col in df.columns:
    print(f"  {col}: {first_row[col]} ({type(first_row[col]).__name__})")

# 測試計算器
print(f"\n\n=== 測試計算器 ===")
settings = Settings()
calculator = SafetyStockCalculator(settings)

# 準備計算參數
article = first_row.get("Article", "TEST001")
site = first_row.get("Site", "001")
shop_class = first_row.get("Class", "A")
last_month_qty = float(first_row.get("Last_Month_Sold_Qty", 100))
last_2_month_qty = float(first_row.get("Last_2_Month_Sold_Qty", 150))
supply_source = first_row.get("Supply Source", "1")
moq = float(first_row.get("MOQ", 10))

print(f"Article: {article}")
print(f"Site: {site}")
print(f"Class: {shop_class}")
print(f"Last Month Qty: {last_month_qty}")
print(f"Last 2 Month Qty: {last_2_month_qty}")

# 準備 Launch Date
launch_date = None
if "Launch Date" in first_row:
    raw_launch_date = first_row["Launch Date"]
    if not pd.isna(raw_launch_date):
        if hasattr(raw_launch_date, 'date'):
            launch_date = raw_launch_date.date()
        else:
            launch_date = raw_launch_date
        print(f"Launch Date: {launch_date} ({type(launch_date).__name__})")

try:
    result = calculator.calculate_safety_stock(
        article=article,
        site=site,
        shop_class=shop_class,
        last_month_qty=last_month_qty,
        last_2_month_qty=last_2_month_qty,
        supply_source=supply_source,
        moq=moq,
        launch_date=launch_date
    )
    print(f"\n✓ 計算成功！")
    print(f"Avg Daily Sales: {result.get('Avg_Daily_Sales')}")
    print(f"Suggested Safety Stock: {result.get('Suggested_Safety_Stock')}")
    print(f"Notes: {result.get('Notes', '')[:200]}...")
except Exception as e:
    print(f"\n✗ 計算失敗：{e}")
    import traceback
    traceback.print_exc()
