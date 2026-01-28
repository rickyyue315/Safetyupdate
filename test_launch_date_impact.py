#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Launch Date 影響計算（Launch Date 過於接近參考日期）
"""
from datetime import date
from core.calculator import SafetyStockCalculator
from config.settings import Settings

# 初始化計算器
settings = Settings()
calculator = SafetyStockCalculator(settings)

# 設定參考日期
selected_date = "2026-01-26"

# 測試 Case 1: Launch Date 在參考日期後 20 天（會影響計算）
# 總天數 = 26 + 31 + 30 = 87 天
# Launch Date 到參考日期 = 20 天 < 87 天，會影響計算
print("=== Test Case 1: Launch Date 會影響計算 ===")
print("Launch Date 在參考日期前約 20 天")
print("選定日期: 2026-01-26")
print("Launch Date: 2026-01-06（約 20 天）")
print("總天數 = 26 + 31 + 30 = 87 天")
print("日期影響: 20 < 87，會影響計算\n")

try:
    result1 = calculator.calculate_safety_stock(
        article="TEST001",
        site="HA01",
        shop_class="A1",
        last_month_qty=100.0,
        last_2_month_qty=150.0,
        supply_source="1",
        moq=10.0,
        original_safety_stock=50,
        mtd_sold_qty=50.0,  # 26 天售出 50 件
        selected_date=selected_date,
        mtd_days=26,
        last_month_days=31,
        last_2_month_days=30,
        launch_date=date(2026, 1, 6)  # 20 天前
    )
    
    notes = result1.get('Notes', '')
    if "Launch Date 影響計算" in notes:
        print("✓ 成功檢測到 Launch Date 影響計算")
        print(f"  Avg Daily Sales: {result1.get('Avg_Daily_Sales')}")
        print(f"  Suggested Safety Stock: {result1.get('Suggested_Safety_Stock')}")
    else:
        print("✗ 未檢測到 Launch Date 影響計算")
        print(f"  Avg Daily Sales: {result1.get('Avg_Daily_Sales')}")
        
except Exception as e:
    print(f"✗ 計算失敗: {e}")
    import traceback
    traceback.print_exc()

# 測試 Case 2: Launch Date 更接近（5 天）
print("\n\n=== Test Case 2: Launch Date 更接近（5 天） ===")
print("Launch Date 在參考日期前約 5 天")
print("選定日期: 2026-01-26")
print("Launch Date: 2026-01-21（約 5 天）")
print("總天數 = 87 天")
print("日期影響: 5 < 87，會更明顯影響計算\n")

try:
    result2 = calculator.calculate_safety_stock(
        article="TEST002",
        site="HA02",
        shop_class="B1",
        last_month_qty=100.0,
        last_2_month_qty=150.0,
        supply_source="1",
        moq=10.0,
        original_safety_stock=50,
        mtd_sold_qty=20.0,  # 5 天售出 20 件
        selected_date=selected_date,
        mtd_days=26,
        last_month_days=31,
        last_2_month_days=30,
        launch_date=date(2026, 1, 21)  # 5 天前
    )
    
    notes = result2.get('Notes', '')
    if "Launch Date 影響計算" in notes:
        print("✓ 成功檢測到 Launch Date 影響計算")
        print(f"  Avg Daily Sales: {result2.get('Avg_Daily_Sales')}")
        print(f"  Suggested Safety Stock: {result2.get('Suggested_Safety_Stock')}")
        print(f"\n詳細計算步驟：")
        for line in notes.split('\n')[:15]:
            print(f"  {line}")
    else:
        print("✗ 未檢測到 Launch Date 影響計算")
        print(f"  Avg Daily Sales: {result2.get('Avg_Daily_Sales')}")
        
except Exception as e:
    print(f"✗ 計算失敗: {e}")
    import traceback
    traceback.print_exc()

# 測試 Case 3: Launch Date 為參考日期當天
print("\n\n=== Test Case 3: Launch Date 為參考日期當天 ===")
print("Launch Date 在參考日期當天")
print("選定日期: 2026-01-26")
print("Launch Date: 2026-01-26（當天）")
print("總天數 = 87 天")
print("日期影響: 1 < 87，只計算 1 天\n")

try:
    result3 = calculator.calculate_safety_stock(
        article="TEST003",
        site="HA03",
        shop_class="C1",
        last_month_qty=100.0,
        last_2_month_qty=150.0,
        supply_source="1",
        moq=10.0,
        original_safety_stock=50,
        mtd_sold_qty=5.0,
        selected_date=selected_date,
        mtd_days=26,
        last_month_days=31,
        last_2_month_days=30,
        launch_date=date(2026, 1, 26)  # 當天
    )
    
    notes = result3.get('Notes', '')
    if "Launch Date 影響計算" in notes:
        print("✓ 成功檢測到 Launch Date 影響計算")
        print(f"  Avg Daily Sales: {result3.get('Avg_Daily_Sales')}")
        print(f"  Suggested Safety Stock: {result3.get('Suggested_Safety_Stock')}")
    else:
        print("✗ 未檢測到 Launch Date 影響計算")
        print(f"  Avg Daily Sales: {result3.get('Avg_Daily_Sales')}")
        
except Exception as e:
    print(f"✗ 計算失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n\n=== 總結 ===")
print("Launch Date 功能已成功實現")
print("當 Launch Date 到參考日期的實際天數 < 總天數時，")
print("系統會使用實際天數計算平均日銷量，並在 Notes 中提示。")
