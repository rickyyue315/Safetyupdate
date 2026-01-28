# -*- coding: utf-8 -*-
"""
測試 MCH2 數字轉換功能

驗證數字類型的 MCH2 值是否正確轉換為 4 位數字串格式
"""

import pandas as pd
import sys
import io

# 設定標準輸出為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_mch2_conversion():
    """測試 MCH2 數字轉換功能"""
    
    print("=" * 80)
    print("測試 MCH2 數字轉換功能")
    print("=" * 80)
    
    # 建立測試資料
    test_data = {
        'MCH2': [302, 103, 403, 703, 301, None, "", "0302", "103"],
        'Class': ['AA', 'B1', 'C1', 'D1', 'A1', 'A2', 'A3', 'AA', 'B1']
    }
    df = pd.DataFrame(test_data)
    
    print("\n原始資料:")
    print(df)
    
    # 應用轉換邏輯
    df['MCH2_Converted'] = df['MCH2'].apply(
        lambda x: str(int(x)).zfill(4) if pd.notna(x) and str(x).strip() != "" else ""
    )
    
    print("\n轉換後資料:")
    print(df)
    
    # 驗證轉換結果
    print("\n驗證轉換結果:")
    test_cases = [
        (0, 302, "0302"),
        (1, 103, "0103"),
        (2, 403, "0403"),
        (3, 703, "0703"),
        (4, 301, "0301"),
        (5, None, ""),
        (6, "", ""),
        (7, "0302", "0302"),
        (8, "103", "0103"),
    ]
    
    all_passed = True
    for idx, original, expected in test_cases:
        actual = df.loc[idx, 'MCH2_Converted']
        if actual == expected:
            print(f"  ✓ 測試 {idx + 1}: {original} → {actual} (預期: {expected})")
        else:
            print(f"  ✗ 測試 {idx + 1}: {original} → {actual} (預期: {expected})")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ 所有測試通過！")
    else:
        print("✗ 部分測試失敗！")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    test_mch2_conversion()
