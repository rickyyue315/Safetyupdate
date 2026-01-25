"""
測試 Class 欄位名稱映射功能
"""
import pandas as pd
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.data_processor import DataProcessor
from core.constants import FIELD_CLASS


def test_class_column_variations():
    """
    測試不同大小寫的 Class 欄位名稱是否能正確映射
    """
    # 測試資料 - 使用不同的欄位名稱變體
    test_cases = [
        {
            "name": "小寫 'class'",
            "columns": ["Article", "Site", "class", "Last Month Sold Qty", 
                       "Last 2 Month Sold Qty", "Supply Source", "MOQ"],
            "expected": FIELD_CLASS
        },
        {
            "name": "大寫 'CLASS'",
            "columns": ["Article", "Site", "CLASS", "Last Month Sold Qty",
                       "Last 2 Month Sold Qty", "Supply Source", "MOQ"],
            "expected": FIELD_CLASS
        },
        {
            "name": "標準 'Class'",
            "columns": ["Article", "Site", "Class", "Last Month Sold Qty",
                       "Last 2 Month Sold Qty", "Supply Source", "MOQ"],
            "expected": FIELD_CLASS
        },
        {
            "name": "Shop Class",
            "columns": ["Article", "Site", "Shop Class", "Last Month Sold Qty",
                       "Last 2 Month Sold Qty", "Supply Source", "MOQ"],
            "expected": FIELD_CLASS
        },
        {
            "name": "小寫 shop class",
            "columns": ["Article", "Site", "shop class", "Last Month Sold Qty",
                       "Last 2 Month Sold Qty", "Supply Source", "MOQ"],
            "expected": FIELD_CLASS
        }
    ]
    
    print("開始測試 Class 欄位名稱映射...")
    print("=" * 60)
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n測試案例: {test_case['name']}")
        print(f"原始欄位: {test_case['columns']}")
        
        # 建立測試 DataFrame
        df = pd.DataFrame(columns=test_case['columns'])
        
        # 標準化欄位名稱
        df_normalized = DataProcessor.normalize_column_names(df)
        
        # 檢查結果
        if test_case['expected'] in df_normalized.columns:
            print(f"✅ 通過 - 欄位已正確映射為 '{test_case['expected']}'")
            print(f"   標準化後欄位: {list(df_normalized.columns)}")
        else:
            print(f"❌ 失敗 - 預期欄位 '{test_case['expected']}' 未找到")
            print(f"   標準化後欄位: {list(df_normalized.columns)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有測試通過！")
    else:
        print("❌ 部分測試失敗！")
    
    return all_passed


def test_validate_required_columns():
    """
    測試使用 'class' 欄位名稱時，驗證功能是否正常
    """
    print("\n" + "=" * 60)
    print("測試必要欄位驗證...")
    print("=" * 60)
    
    # 使用 'class' 欄位名稱建立測試資料
    test_data = pd.DataFrame({
        "Article": ["SKU001", "SKU002"],
        "Site": ["S001", "S002"],
        "class": ["A1", "B1"],  # 使用小寫
        "Last Month Sold Qty": [100, 200],
        "Last 2 Month Sold Qty": [200, 400],
        "Supply Source": ["1", "2"],
        "MOQ": [10, 20]
    })
    
    print(f"\n原始欄位: {list(test_data.columns)}")
    
    # 標準化欄位名稱
    test_data = DataProcessor.normalize_column_names(test_data)
    print(f"標準化後欄位: {list(test_data.columns)}")
    
    # 驗證必要欄位
    is_valid = DataProcessor.validate_required_columns(test_data)
    
    if is_valid:
        print("✅ 驗證通過 - 所有必要欄位都存在")
        return True
    else:
        missing = DataProcessor.get_missing_columns(test_data)
        print(f"❌ 驗證失敗 - 缺少欄位: {missing}")
        return False


if __name__ == "__main__":
    # 執行所有測試
    test1_passed = test_class_column_variations()
    test2_passed = test_validate_required_columns()
    
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)
    print(f"欄位名稱映射測試: {'✅ 通過' if test1_passed else '❌ 失敗'}")
    print(f"必要欄位驗證測試: {'✅ 通過' if test2_passed else '❌ 失敗'}")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("\n🎉 所有測試通過！Class 欄位名稱映射功能正常運作。")
        sys.exit(0)
    else:
        print("\n⚠️ 部分測試失敗，請檢查程式碼。")
        sys.exit(1)
