"""
測試日期感知計算模式的修正
"""
from datetime import date
from core.data_processor import DateCalculator
from core.constants import (
    FIELD_SELECTED_DATE,
    FIELD_MTD_DAYS,
    FIELD_LAST_MONTH_DAYS,
    FIELD_LAST_2_MONTH_DAYS
)

def test_date_calculation():
    """測試日期計算功能"""
    
    # 測試案例 1: 2025-12-23 (原始問題案例)
    print("=" * 60)
    print("測試案例 1: 2025-12-23")
    print("=" * 60)
    
    selected_date = date(2025, 12, 23)
    date_params = DateCalculator.calculate_date_parameters(selected_date)
    
    print(f"選定日期: {date_params[FIELD_SELECTED_DATE]}")
    print(f"當月月份: {date_params['current_month']}月")
    print(f"當月天數 (MTD): {date_params[FIELD_MTD_DAYS]} 天")
    print(f"上月: {date_params['last_month']}月, 天數: {date_params[FIELD_LAST_MONTH_DAYS]} 天")
    print(f"前兩月: {date_params['last_2_month']}月, 天數: {date_params[FIELD_LAST_2_MONTH_DAYS]} 天")
    
    # 驗證結果
    assert date_params['current_month'] == 12, "當月應該是 12 月"
    assert date_params[FIELD_MTD_DAYS] == 23, "MTD 天數應該是 23 天"
    assert date_params['last_month'] == 11, "上月應該是 11 月"
    assert date_params[FIELD_LAST_MONTH_DAYS] == 30, "上月天數應該是 30 天"
    assert date_params['last_2_month'] == 10, "前兩月應該是 10 月"
    assert date_params[FIELD_LAST_2_MONTH_DAYS] == 31, "前兩月天數應該是 31 天"
    
    print("[PASS] 測試案例 1 通過！\n")
    
    # 測試案例 2: 2026-01-27 (當前日期)
    print("=" * 60)
    print("測試案例 2: 2026-01-27")
    print("=" * 60)
    
    selected_date = date(2026, 1, 27)
    date_params = DateCalculator.calculate_date_parameters(selected_date)
    
    print(f"選定日期: {date_params[FIELD_SELECTED_DATE]}")
    print(f"當月月份: {date_params['current_month']}月")
    print(f"當月天數 (MTD): {date_params[FIELD_MTD_DAYS]} 天")
    print(f"上月: {date_params['last_month']}月, 天數: {date_params[FIELD_LAST_MONTH_DAYS]} 天")
    print(f"前兩月: {date_params['last_2_month']}月, 天數: {date_params[FIELD_LAST_2_MONTH_DAYS]} 天")
    
    # 驗證結果
    assert date_params['current_month'] == 1, "當月應該是 1 月"
    assert date_params[FIELD_MTD_DAYS] == 27, "MTD 天數應該是 27 天"
    assert date_params['last_month'] == 12, "上月應該是 12 月"
    assert date_params[FIELD_LAST_MONTH_DAYS] == 31, "上月天數應該是 31 天"
    assert date_params['last_2_month'] == 11, "前兩月應該是 11 月"
    assert date_params[FIELD_LAST_2_MONTH_DAYS] == 30, "前兩月天數應該是 30 天"
    
    print("[PASS] 測試案例 2 通過！\n")
    
    # 測試案例 3: 2026-03-15 (跨年邊界測試)
    print("=" * 60)
    print("測試案例 3: 2026-03-15")
    print("=" * 60)
    
    selected_date = date(2026, 3, 15)
    date_params = DateCalculator.calculate_date_parameters(selected_date)
    
    print(f"選定日期: {date_params[FIELD_SELECTED_DATE]}")
    print(f"當月月份: {date_params['current_month']}月")
    print(f"當月天數 (MTD): {date_params[FIELD_MTD_DAYS]} 天")
    print(f"上月: {date_params['last_month']}月, 天數: {date_params[FIELD_LAST_MONTH_DAYS]} 天")
    print(f"前兩月: {date_params['last_2_month']}月, 天數: {date_params[FIELD_LAST_2_MONTH_DAYS]} 天")
    
    # 驗證結果
    assert date_params['current_month'] == 3, "當月應該是 3 月"
    assert date_params[FIELD_MTD_DAYS] == 15, "MTD 天數應該是 15 天"
    assert date_params['last_month'] == 2, "上月應該是 2 月"
    assert date_params[FIELD_LAST_MONTH_DAYS] == 28, "上月天數應該是 28 天 (2026 不是閏年)"
    assert date_params['last_2_month'] == 1, "前兩月應該是 1 月"
    assert date_params[FIELD_LAST_2_MONTH_DAYS] == 31, "前兩月天數應該是 31 天"
    
    print("[PASS] 測試案例 3 通過！\n")
    
    # 測試案例 4: 2026-01-01 (月初)
    print("=" * 60)
    print("測試案例 4: 2026-01-01 (月初)")
    print("=" * 60)
    
    selected_date = date(2026, 1, 1)
    date_params = DateCalculator.calculate_date_parameters(selected_date)
    
    print(f"選定日期: {date_params[FIELD_SELECTED_DATE]}")
    print(f"當月月份: {date_params['current_month']}月")
    print(f"當月天數 (MTD): {date_params[FIELD_MTD_DAYS]} 天")
    print(f"上月: {date_params['last_month']}月, 天數: {date_params[FIELD_LAST_MONTH_DAYS]} 天")
    print(f"前兩月: {date_params['last_2_month']}月, 天數: {date_params[FIELD_LAST_2_MONTH_DAYS]} 天")
    
    # 驗證結果
    assert date_params['current_month'] == 1, "當月應該是 1 月"
    assert date_params[FIELD_MTD_DAYS] == 1, "MTD 天數應該是 1 天"
    assert date_params['last_month'] == 12, "上月應該是 12 月"
    assert date_params[FIELD_LAST_MONTH_DAYS] == 31, "上月天數應該是 31 天"
    assert date_params['last_2_month'] == 11, "前兩月應該是 11 月"
    assert date_params[FIELD_LAST_2_MONTH_DAYS] == 30, "前兩月天數應該是 30 天"
    
    print("[PASS] 測試案例 4 通過！\n")
    
    print("=" * 60)
    print("[SUCCESS] 所有測試案例都通過了！")
    print("=" * 60)
    print("\n修正摘要:")
    print("- 當月月份現在會正確顯示為選定日期的月份")
    print("- 上月和前兩月的月份也會正確計算")
    print("- 系統現在能夠自動根據選定的日期動態顯示正確的月份名稱")

if __name__ == "__main__":
    test_date_calculation()
