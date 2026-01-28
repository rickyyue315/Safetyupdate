#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Launch Date 日期感知計算功能
"""
import pandas as pd
from datetime import date, datetime
from core.calculator import SafetyStockCalculator
from config.settings import Settings

# 讀取測試文件
print("讀取 Test_26Jan2026.XLSX...")
df = pd.read_excel("Test_26Jan2026.XLSX")

print(f"檔案包含 {len(df)} 行資料\n")

# 初始化計算器和設定
settings = Settings()
calculator = SafetyStockCalculator(settings)

# 選擇參考日期（當前日期）
selected_date = "2026-01-26"  # 從文件名推測的日期
selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

print(f"參考日期: {selected_date_obj}")

# 測試第一行
print(f"\n=== 測試第一行：Article 110269202001 ===")
first_row = df.iloc[0]

article = first_row.get("Article", "TEST001")
site = first_row.get("Site", "001")
shop_class = first_row.get("Class", "A")
mtd_qty = float(first_row.get("MTD Sold Qty", 0))
last_month_qty = float(first_row.get("Last Month Sold Qty", 0))
last_2_month_qty = float(first_row.get("Last 2 Month", 0))
supply_source = first_row.get("Supply source", "1")
moq = float(first_row.get("MOQ", 10))

# 準備 Launch Date
launch_date = None
if not pd.isna(first_row["Launch Date"]):
    raw_ld = first_row["Launch Date"]
    if hasattr(raw_ld, 'date'):
        launch_date = raw_ld.date()
    else:
        launch_date = raw_ld

print(f"Article: {article}")
print(f"Site: {site}")
print(f"Class: {shop_class}")
print(f"MTD Qty: {mtd_qty}")
print(f"Last Month Qty: {last_month_qty}")
print(f"Last 2 Month Qty: {last_2_month_qty}")
print(f"Supply Source: {supply_source}")
print(f"MOQ: {moq}")
print(f"Launch Date: {launch_date} ({type(launch_date).__name__})")

# 計算 MTD、Last Month、Last 2 Month 的天數
# 根據選定的參考日期，計算每個期間的天數
mtd_days = 26  # 1 月到 26 日
last_month_days = 31  # 12 月有 31 天
last_2_month_days = 30  # 11 月有 30 天

print(f"\nMTD Days: {mtd_days}")
print(f"Last Month Days: {last_month_days}")
print(f"Last 2 Month Days: {last_2_month_days}")

print(f"\n正在計算...")
try:
    result = calculator.calculate_safety_stock(
        article=article,
        site=site,
        shop_class=shop_class,
        last_month_qty=last_month_qty,
        last_2_month_qty=last_2_month_qty,
        supply_source=supply_source,
        moq=moq,
        original_safety_stock=first_row.get("Safety Stock"),
        mtd_sold_qty=mtd_qty,
        selected_date=selected_date,
        mtd_days=mtd_days,
        last_month_days=last_month_days,
        last_2_month_days=last_2_month_days,
        launch_date=launch_date
    )
    
    print(f"\n✓ 計算成功！")
    print(f"\nAvg Daily Sales: {result.get('Avg_Daily_Sales')}")
    print(f"Suggested Safety Stock: {result.get('Suggested_Safety_Stock')}")
    print(f"Safety Stock Days: {result.get('Safety_Stock_Days')}")
    
    notes = result.get('Notes', '')
    print(f"\nNotes (前300字):")
    print(notes[:300])
    
    # 檢查是否包含 Launch Date 影響提示
    if "Launch Date 影響計算" in notes:
        print(f"\n✓ 發現 Launch Date 影響計算提示")
    else:
        print(f"\n✗ 未發現 Launch Date 影響計算提示")
        
except Exception as e:
    print(f"\n✗ 計算失敗：{e}")
    import traceback
    traceback.print_exc()

# 現在測試多個記錄
print(f"\n\n=== 測試多個記錄（前 5 行）===")
success_count = 0
error_count = 0

for idx in range(min(5, len(df))):
    row = df.iloc[idx]
    try:
        article = row.get("Article")
        site = row.get("Site")
        
        # 準備 Launch Date
        launch_date = None
        if not pd.isna(row["Launch Date"]):
            ld = row["Launch Date"]
            if hasattr(ld, 'date'):
                launch_date = ld.date()
        
        result = calculator.calculate_safety_stock(
            article=article,
            site=site,
            shop_class=row.get("Class", "A"),
            last_month_qty=float(row.get("Last Month Sold Qty", 0)),
            last_2_month_qty=float(row.get("Last 2 Month", 0)),
            supply_source=row.get("Supply source", "1"),
            moq=float(row.get("MOQ", 10)),
            original_safety_stock=row.get("Safety Stock"),
            mtd_sold_qty=float(row.get("MTD Sold Qty", 0)),
            selected_date=selected_date,
            mtd_days=mtd_days,
            last_month_days=last_month_days,
            last_2_month_days=last_2_month_days,
            launch_date=launch_date
        )
        print(f"✓ {article} - {site}: Avg Daily Sales = {result.get('Avg_Daily_Sales')}")
        success_count += 1
    except Exception as e:
        print(f"✗ {article} - {site}: {e}")
        error_count += 1

print(f"\n成功: {success_count}, 失敗: {error_count}")
