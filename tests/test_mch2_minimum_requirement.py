# -*- coding: utf-8 -*-
"""
測試 MCH2 最低安全庫存要求功能

測試案例：
1. MCH2 = 0302, Class AA, suggested > 12 → 應該使用 12
2. MCH2 = 0302, Class AA, suggested = 8 (< 12) → 應該使用 12
3. MCH2 = 0302, Class B1, suggested = 7 (< 10) → 應該使用 10
4. MCH2 = 0302, Class C1, suggested = 4 (< 6) → 應該使用 6
5. MCH2 = 0302, Class AA, suggested = 15 (>= 12) → 應該使用 15
6. MCH2 = 0303 (不是 0302) → 應該使用標準計算
7. MCH2 = empty/None → 應該使用標準計算
8. MCH2 = 0302, Class AA, mch2 missing → 應該使用標準計算
9. MCH2 = 0302, Class AA, mch2 = "" (empty) → 應該使用標準計算
"""

import sys
import os
import io

# 設定標準輸出為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.calculator import SafetyStockCalculator
from config.settings import Settings


def test_mch2_minimum_requirement():
    """測試 MCH2 最低安全庫存要求功能"""
    
    # 初始化計算器和設定
    settings = Settings()
    calculator = SafetyStockCalculator(settings)
    
    print("=" * 80)
    print("測試 MCH2 最低安全庫存要求功能")
    print("=" * 80)
    
    # 測試案例 1: MCH2 = 0302, Class AA, suggested > 12 → 應該使用 12
    print("\n測試案例 1: MCH2 = 0302, Class AA, suggested = 15 (> 12)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=15,
        mch2="0302",
        shop_class="AA"
    )
    print(f"  輸入: suggested_ss=15, mch2='0302', shop_class='AA'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 15, f"預期 15，實際 {result[0]}"
    assert result[1] == False, f"預期 False，實際 {result[1]}"
    assert result[2] == 12, f"預期 12，實際 {result[2]}"
    print("  ✓ 測試通過：suggested > 12 時，使用 suggested 值")
    
    # 測試案例 2: MCH2 = 0302, Class AA, suggested = 8 (< 12) → 應該使用 12
    print("\n測試案例 2: MCH2 = 0302, Class AA, suggested = 8 (< 12)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=8,
        mch2="0302",
        shop_class="AA"
    )
    print(f"  輸入: suggested_ss=8, mch2='0302', shop_class='AA'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 12, f"預期 12，實際 {result[0]}"
    assert result[1] == True, f"預期 True，實際 {result[1]}"
    assert result[2] == 12, f"預期 12，實際 {result[2]}"
    print("  ✓ 測試通過：suggested < 12 時，使用最低要求 12")
    
    # 測試案例 3: MCH2 = 0302, Class B1, suggested = 7 (< 10) → 應該使用 10
    print("\n測試案例 3: MCH2 = 0302, Class B1, suggested = 7 (< 10)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=7,
        mch2="0302",
        shop_class="B1"
    )
    print(f"  輸入: suggested_ss=7, mch2='0302', shop_class='B1'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 10, f"預期 10，實際 {result[0]}"
    assert result[1] == True, f"預期 True，實際 {result[1]}"
    assert result[2] == 10, f"預期 10，實際 {result[2]}"
    print("  ✓ 測試通過：suggested < 10 時，使用最低要求 10")
    
    # 測試案例 4: MCH2 = 0302, Class C1, suggested = 4 (< 6) → 應該使用 6
    print("\n測試案例 4: MCH2 = 0302, Class C1, suggested = 4 (< 6)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=4,
        mch2="0302",
        shop_class="C1"
    )
    print(f"  輸入: suggested_ss=4, mch2='0302', shop_class='C1'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 6, f"預期 6，實際 {result[0]}"
    assert result[1] == True, f"預期 True，實際 {result[1]}"
    assert result[2] == 6, f"預期 6，實際 {result[2]}"
    print("  ✓ 測試通過：suggested < 6 時，使用最低要求 6")
    
    # 測試案例 5: MCH2 = 0302, Class AA, suggested = 12 (= 12) → 應該使用 12
    print("\n測試案例 5: MCH2 = 0302, Class AA, suggested = 12 (= 12)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=12,
        mch2="0302",
        shop_class="AA"
    )
    print(f"  輸入: suggested_ss=12, mch2='0302', shop_class='AA'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 12, f"預期 12，實際 {result[0]}"
    assert result[1] == False, f"預期 False，實際 {result[1]}"
    assert result[2] == 12, f"預期 12，實際 {result[2]}"
    print("  ✓ 測試通過：suggested = 12 時，使用 suggested 值（不應用約束）")
    
    # 測試案例 6: MCH2 = 0303 (不是 0302) → 應該使用標準計算
    print("\n測試案例 6: MCH2 = 0303 (不是 0302)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=8,
        mch2="0303",
        shop_class="AA"
    )
    print(f"  輸入: suggested_ss=8, mch2='0303', shop_class='AA'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 8, f"預期 8，實際 {result[0]}"
    assert result[1] == False, f"預期 False，實際 {result[1]}"
    assert result[2] == 0, f"預期 0，實際 {result[2]}"
    print("  ✓ 測試通過：MCH2 不是 0302 時，使用標準計算")
    
    # 測試案例 7: MCH2 = None → 應該使用標準計算
    print("\n測試案例 7: MCH2 = None")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=8,
        mch2=None,
        shop_class="AA"
    )
    print(f"  輸入: suggested_ss=8, mch2=None, shop_class='AA'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 8, f"預期 8，實際 {result[0]}"
    assert result[1] == False, f"預期 False，實際 {result[1]}"
    assert result[2] == 0, f"預期 0，實際 {result[2]}"
    print("  ✓ 測試通過：MCH2 為 None 時，使用標準計算")
    
    # 測試案例 8: MCH2 = "" (空字串) → 應該使用標準計算
    print("\n測試案例 8: MCH2 = '' (空字串)")
    result = calculator.apply_mch2_minimum_requirement(
        suggested_ss=8,
        mch2="",
        shop_class="AA"
    )
    print(f"  輸入: suggested_ss=8, mch2='', shop_class='AA'")
    print(f"  輸出: adjusted_ss={result[0]}, applied={result[1]}, minimum={result[2]}")
    assert result[0] == 8, f"預期 8，實際 {result[0]}"
    assert result[1] == False, f"預期 False，實際 {result[1]}"
    assert result[2] == 0, f"預期 0，實際 {result[2]}"
    print("  ✓ 測試通過：MCH2 為空字串時，使用標準計算")
    
    # 測試案例 9: 測試所有 Shop Class
    print("\n測試案例 9: 測試所有 Shop Class 的最低要求")
    test_cases = [
        ("AA", 12, 15, 15, False),  # suggested >= minimum
        ("A1", 12, 8, 12, True),   # suggested < minimum
        ("A2", 12, 10, 12, True),  # suggested < minimum
        ("A3", 12, 11, 12, True),  # suggested < minimum
        ("B1", 10, 8, 10, True),   # suggested < minimum
        ("B2", 10, 12, 12, False), # suggested >= minimum
        ("C1", 6, 4, 6, True),     # suggested < minimum
        ("C2", 6, 7, 7, False),    # suggested >= minimum
        ("D1", 6, 5, 6, True),     # suggested < minimum
    ]
    
    for shop_class, minimum, suggested, expected_ss, expected_applied in test_cases:
        result = calculator.apply_mch2_minimum_requirement(
            suggested_ss=suggested,
            mch2="0302",
            shop_class=shop_class
        )
        print(f"  Class {shop_class}: suggested={suggested}, minimum={minimum} → {result[0]} (applied={result[1]})")
        assert result[0] == expected_ss, f"Class {shop_class}: 預期 {expected_ss}，實際 {result[0]}"
        assert result[1] == expected_applied, f"Class {shop_class}: 預期 applied={expected_applied}，實際 {result[1]}"
        assert result[2] == minimum, f"Class {shop_class}: 預期 minimum={minimum}，實際 {result[2]}"
    
    print("  ✓ 所有 Shop Class 測試通過")
    
    print("\n" + "=" * 80)
    print("✓ 所有測試案例通過！")
    print("=" * 80)


if __name__ == "__main__":
    test_mch2_minimum_requirement()
