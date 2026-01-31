"""
測試店舖類型配置模式 (Shop Type Configuration Mode)
"""
import sys
sys.path.insert(0, '.')

from config.settings import Settings
from core.calculator import SafetyStockCalculator
from core.constants import SHOP_TYPE_SS_CONFIG

def test_shop_type_safety_stock():
    """測試店舖類型安全庫存查詢功能"""
    
    print("=" * 80)
    print("測試 1: 店舖類型安全庫存查詢功能")
    print("=" * 80)
    
    # 建立計算器
    settings = Settings(use_shop_type_mode=True)
    calculator = SafetyStockCalculator(settings)
    
    # 測試案例
    test_cases = [
        # HK 區域
        ("HK", "AA", "XL", 18),
        ("HK", "A1", "L", 18),
        ("HK", "A2", "M", 18),
        ("HK", "B1", "L", 18),
        ("HK", "B2", "M", 12),
        ("HK", "B1", "S", 12),
        ("HK", "C1", "M", 12),
        ("HK", "C2", "XS", 0),
        ("HK", "D1", "L", 9),
        ("HK", "D1", "M", 6),
        
        # MO 區域
        ("MO", "AA", "XL", 24),
        ("MO", "A1", "L", 24),
        ("MO", "B1", "L", 18),
        ("MO", "B2", "S", 12),
        ("MO", "C1", "L", 12),
        ("MO", "D1", "M", 6),
    ]
    
    print("\n測試查詢結果:")
    print(f"{'區域':<6} {'店舖等級':<8} {'貨場面積':<8} {'預期結果':<8} {'實際結果':<8} {'狀態':<6}")
    print("-" * 60)
    
    all_passed = True
    for region, shop_class, shop_size, expected in test_cases:
        result = calculator.get_shop_type_safety_stock(region, shop_class, shop_size)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"{region:<6} {shop_class:<8} {shop_size:<8} {expected:<8} {result if result is not None else 'None':<8} {status:<6}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有測試通過")
    else:
        print("✗ 部分測試失敗")
    print("=" * 60)


def test_shop_type_calculation():
    """測試店舖類型模式的完整計算流程"""
    
    print("\n" + "=" * 80)
    print("測試 2: 店舖類型模式完整計算流程")
    print("=" * 80)
    
    # 建立啟用店舖類型模式的設定
    settings = Settings(use_shop_type_mode=True)
    calculator = SafetyStockCalculator(settings)
    
    # 測試資料
    test_data = {
        "article": "TEST001",
        "site": "HA02",
        "shop_class": "B2",
        "last_month_qty": 100.0,
        "last_2_month_qty": 150.0,
        "supply_source": "1",
        "moq": 6.0,
        "original_safety_stock": 10.0,
        "region": "HK",
        "shop_size": "M"
    }
    
    print("\n輸入資料:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # 執行計算
    result = calculator.calculate_safety_stock(
        article=test_data["article"],
        site=test_data["site"],
        shop_class=test_data["shop_class"],
        last_month_qty=test_data["last_month_qty"],
        last_2_month_qty=test_data["last_2_month_qty"],
        supply_source=test_data["supply_source"],
        moq=test_data["moq"],
        original_safety_stock=test_data["original_safety_stock"],
        region=test_data["region"],
        shop_size=test_data["shop_size"]
    )
    
    print("\n計算結果:")
    print(f"  建議安全庫存: {result['Suggested_Safety_Stock']}")
    print(f"  安全庫存天數: {result['Safety_Stock_Days']}")
    print(f"  計算模式: {result['Calculation_Mode']}")
    print(f"  約束類型: {result['Constraint_Applied']}")
    print(f"  平均日銷量: {result['Avg_Daily_Sales']}")
    
    print("\n計算說明:")
    print(result['Notes'])
    
    # 驗證結果
    expected_ss = 12  # HK B2 M 應該是 12
    if result['Suggested_Safety_Stock'] == expected_ss:
        print(f"\n✓ 計算結果正確: {result['Suggested_Safety_Stock']} == {expected_ss}")
    else:
        print(f"\n✗ 計算結果錯誤: {result['Suggested_Safety_Stock']} != {expected_ss}")
    
    if result['Calculation_Mode'] == "Shop Type Configuration":
        print("✓ 計算模式正確: Shop Type Configuration")
    else:
        print(f"✗ 計算模式錯誤: {result['Calculation_Mode']}")


def test_shop_type_config_display():
    """顯示店舖類型配置表"""
    
    print("\n" + "=" * 80)
    print("店舖類型安全庫存配置表")
    print("=" * 80)
    
    for region, classes in SHOP_TYPE_SS_CONFIG.items():
        print(f"\n區域: {region}")
        print("-" * 60)
        for class_cat, sizes in classes.items():
            print(f"  店舖等級 {class_cat}:")
            for size, qty in sizes.items():
                print(f"    {size}: {qty} 件")


def test_standard_mode_not_affected():
    """測試標準模式不受影響"""
    
    print("\n" + "=" * 80)
    print("測試 3: 標準模式不受影響")
    print("=" * 80)
    
    # 建立未啟用店舖類型模式的設定
    settings = Settings(use_shop_type_mode=False)
    calculator = SafetyStockCalculator(settings)
    
    # 測試資料（包含區域和貨場面積，但不應該使用）
    result = calculator.calculate_safety_stock(
        article="TEST002",
        site="HA02",
        shop_class="B2",
        last_month_qty=100.0,
        last_2_month_qty=150.0,
        supply_source="1",
        moq=6.0,
        original_safety_stock=10.0,
        region="HK",
        shop_size="M"
    )
    
    print("\n計算結果:")
    print(f"  建議安全庫存: {result['Suggested_Safety_Stock']}")
    print(f"  計算模式: {result['Calculation_Mode']}")
    print(f"  約束類型: {result['Constraint_Applied']}")
    
    # 驗證結果應該使用標準公式，而不是店舖類型配置
    if result['Calculation_Mode'] != "Shop Type Configuration":
        print("\n✓ 標準模式正常運作，未受店舖類型模式影響")
    else:
        print("\n✗ 錯誤：標準模式被店舖類型模式影響")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("店舖類型配置模式測試")
    print("=" * 80)
    
    # 測試 1: 查詢功能
    test_shop_type_safety_stock()
    
    # 顯示配置表
    test_shop_type_config_display()
    
    # 測試 2: 完整計算
    test_shop_type_calculation()
    
    # 測試 3: 標準模式不受影響
    test_standard_mode_not_affected()
    
    print("\n" + "=" * 80)
    print("測試完成")
    print("=" * 80)
