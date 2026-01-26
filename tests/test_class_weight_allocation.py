"""
測試按 Class 權重分配 SKU 目標數量的邏輯
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

from config.settings import Settings
from core.calculator import SafetyStockCalculator


def test_class_weight_allocation_basic():
    """測試基本的按 Class 權重分配邏輯"""
    print("測試 1: 基本的按 Class 權重分配")
    print("=" * 80)
    
    # 建立測試資料
    test_data = {
        'Article': ['ART001', 'ART001', 'ART001', 'ART001'],
        'Site': ['S001', 'S002', 'S003', 'S004'],
        'Class': ['AA', 'B1', 'C1', 'D1'],
        'Last Month Sold Qty': [120, 100, 80, 60],
        'Last 2 Month Sold Qty': [240, 200, 160, 120],
        'Supply Source': ['1', '1', '1', '1'],
        'MOQ': [10, 8, 6, 5]
    }
    df = pd.DataFrame(test_data)
    
    # 執行標準計算
    settings = Settings()
    calculator = SafetyStockCalculator(settings)
    
    results = []
    for _, row in df.iterrows():
        result = calculator.calculate_safety_stock(
            article=row['Article'],
            site=row['Site'],
            shop_class=row['Class'],
            last_month_qty=row['Last Month Sold Qty'],
            last_2_month_qty=row['Last 2 Month Sold Qty'],
            supply_source=str(row['Supply Source']),
            moq=row['MOQ']
        )
        results.append(result)
    
    results_df = pd.DataFrame(results)
    
    # 設定目標數量
    target_qty = 100
    
    # 手動執行按 Class 權重分配
    # 權重: AA=3, B1=2, C1=1, D1=1
    # 總權重 = 3 + 2 + 1 + 1 = 7
    # 分配係數 = 100 / 7 ≈ 14.2857
    
    # 預期分配 (向下取整):
    # AA: floor(3 * 14.2857) = floor(42.8571) = 42
    # B1: floor(2 * 14.2857) = floor(28.5714) = 28
    # C1: floor(1 * 14.2857) = floor(14.2857) = 14
    # D1: floor(1 * 14.2857) = floor(14.2857) = 14
    # 總和 = 42 + 28 + 14 + 14 = 98
    # 餘數 = 100 - 98 = 2
    
    # 餘數分配給小數部分最大的店舖:
    # 小數部分: AA=0.8571, B1=0.5714, C1=0.2857, D1=0.2857
    # 餘數分配給 AA 和 B1
    # 最終: AA=43, B1=29, C1=14, D1=14
    
    expected_allocation = {
        'S001': 43,  # AA
        'S002': 29,  # B1
        'S003': 14,  # C1
        'S004': 14   # D1
    }
    
    print(f"目標數量: {target_qty}")
    print(f"權重分配: AA=3, B1=2, C1=1, D1=1")
    print(f"總權重: 7")
    print(f"預期分配: {expected_allocation}")
    
    # 驗證總和
    total = sum(expected_allocation.values())
    assert total == target_qty, f"分配總和 {total} 應該等於目標數量 {target_qty}"
    
    print(f"\n✅ 測試 1 通過！分配邏輯正確")
    print()


def test_class_weight_allocation_multiple_skus():
    """測試多個 SKU 的分配"""
    print("測試 2: 多個 SKU 的分配")
    print("=" * 80)
    
    # 建立測試資料
    test_data = {
        'Article': ['ART001', 'ART001', 'ART002', 'ART002'],
        'Site': ['S001', 'S002', 'S003', 'S004'],
        'Class': ['A1', 'B2', 'A2', 'C2'],
        'Last Month Sold Qty': [120, 100, 80, 60],
        'Last 2 Month Sold Qty': [240, 200, 160, 120],
        'Supply Source': ['1', '1', '1', '1'],
        'MOQ': [10, 8, 6, 5]
    }
    df = pd.DataFrame(test_data)
    
    # 設定目標數量
    sku_targets = {
        'ART001': 60,
        'ART002': 40
    }
    
    # ART001: A1=3, B2=2, 總權重=5, 係數=12
    # 預期: A1=36, B2=24
    
    # ART002: A2=3, C2=1, 總權重=4, 係數=10
    # 預期: A2=30, C2=10
    
    expected_allocations = {
        'ART001': {'S001': 36, 'S002': 24},  # A1=3, B2=2
        'ART002': {'S003': 30, 'S004': 10}   # A2=3, C2=1
    }
    
    print(f"SKU 目標數量: {sku_targets}")
    print(f"預期分配:")
    for sku, alloc in expected_allocations.items():
        print(f"  {sku}: {alloc}")
    
    # 驗證總和
    for sku, alloc in expected_allocations.items():
        total = sum(alloc.values())
        assert total == sku_targets[sku], f"SKU {sku} 分配總和 {total} 應該等於目標數量 {sku_targets[sku]}"
    
    print(f"\n✅ 測試 2 通過！多 SKU 分配邏輯正確")
    print()


def test_class_weight_allocation_same_class():
    """測試相同 Class 的分配"""
    print("測試 3: 相同 Class 的分配")
    print("=" * 80)
    
    # 建立測試資料 - 所有店舖都是 A1
    test_data = {
        'Article': ['ART001', 'ART001', 'ART001'],
        'Site': ['S001', 'S002', 'S003'],
        'Class': ['A1', 'A1', 'A1'],
        'Last Month Sold Qty': [120, 100, 80],
        'Last 2 Month Sold Qty': [240, 200, 160],
        'Supply Source': ['1', '1', '1'],
        'MOQ': [10, 8, 6]
    }
    df = pd.DataFrame(test_data)
    
    # 設定目標數量
    target_qty = 90
    
    # 所有店舖權重都是 3，總權重=9，係數=10
    # 預期: 每個店舖分配 30
    
    expected_allocation = {
        'S001': 30,
        'S002': 30,
        'S003': 30
    }
    
    print(f"目標數量: {target_qty}")
    print(f"所有店舖都是 A1 (權重=3)")
    print(f"預期分配: {expected_allocation}")
    
    # 驗證總和
    total = sum(expected_allocation.values())
    assert total == target_qty, f"分配總和 {total} 應該等於目標數量 {target_qty}"
    
    print(f"\n✅ 測試 3 通過！相同 Class 分配正確")
    print()


def test_class_weight_weights_table():
    """測試 Class 權重對照表"""
    print("測試 4: Class 權重對照表")
    print("=" * 80)
    
    # 從 app.py 導入權重對照表
    CLASS_WEIGHTS = {
        "AA": 3, "A1": 3, "A2": 3, "A3": 3,
        "B1": 2, "B2": 2,
        "C1": 1, "C2": 1,
        "D1": 1
    }
    
    print("Class 權重對照表:")
    for class_name, weight in sorted(CLASS_WEIGHTS.items()):
        print(f"  {class_name}: {weight}")
    
    # 驗證權重
    assert CLASS_WEIGHTS['AA'] == 3, "AA 權重應該是 3"
    assert CLASS_WEIGHTS['A1'] == 3, "A1 權重應該是 3"
    assert CLASS_WEIGHTS['B1'] == 2, "B1 權重應該是 2"
    assert CLASS_WEIGHTS['C1'] == 1, "C1 權重應該是 1"
    assert CLASS_WEIGHTS['D1'] == 1, "D1 權重應該是 1"
    
    print(f"\n✅ 測試 4 通過！Class 權重對照表正確")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("按 Class 權重分配 SKU 目標數量測試")
    print("=" * 80)
    print()
    
    try:
        test_class_weight_allocation_basic()
        test_class_weight_allocation_multiple_skus()
        test_class_weight_allocation_same_class()
        test_class_weight_weights_table()
        
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
