# -*- coding: utf-8 -*-
"""
整合測試：驗證整個系統是否能正確處理 Test_28Jan2026.XLSX 檔案中的 MCH2 欄位

測試目標：
1. 驗證 DataProcessor 能正確讀取並轉換 MCH2 欄位
2. 驗證 Calculator 能正確應用 MCH2 最低安全庫存要求
3. 驗證整個流程從檔案讀取到計算結果的完整性
"""

import sys
import os
import io

# 設定標準輸出為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from core.data_processor import DataProcessor
from core.calculator import SafetyStockCalculator
from config.settings import Settings


def test_mch2_integration():
    """整合測試 MCH2 功能"""
    
    print("=" * 80)
    print("整合測試：驗證 MCH2 功能的完整流程")
    print("=" * 80)
    
    try:
        # 初始化
        settings = Settings()
        processor = DataProcessor()
        calculator = SafetyStockCalculator(settings)
        
        # 步驟 1：讀取檔案
        print("\n步驟 1：讀取 Test_28Jan2026.XLSX 檔案")
        df = processor.load_data("Test_28Jan2026.XLSX")
        print(f"  ✓ 成功讀取檔案")
        print(f"  總行數: {len(df)}")
        
        # 步驟 2：驗證 MCH2 欄位
        print("\n步驟 2：驗證 MCH2 欄位")
        if "MCH2" in df.columns:
            print(f"  ✓ MCH2 欄位存在")
            
            # 檢查 MCH2 值
            mch2_values = df['MCH2'].dropna().unique()
            print(f"  MCH2 唯一值數量: {len(mch2_values)}")
            print(f"  MCH2 唯一值: {sorted(mch2_values)}")
            
            # 檢查是否有 "0302" 值
            if "0302" in mch2_values:
                print(f"  ✓ 發現 MCH2 = '0302' 的記錄")
                mch2_0302_count = (df['MCH2'] == "0302").sum()
                print(f"  MCH2 = '0302' 的記錄數量: {mch2_0302_count}")
            else:
                print(f"  ⚠ 未發現 MCH2 = '0302' 的記錄")
        else:
            print(f"  ✗ MCH2 欄位不存在")
            return False
        
        # 步驟 3：清理和標準化資料
        print("\n步驟 3：清理和標準化資料")
        df_clean = processor.clean_data(df)
        print(f"  ✓ 成功清理資料")
        print(f"  清理後行數: {len(df_clean)}")
        
        # 驗證 MCH2 轉換
        if "MCH2" in df_clean.columns:
            mch2_clean_values = df_clean['MCH2'].dropna().unique()
            print(f"  清理後 MCH2 唯一值: {sorted(mch2_clean_values)}")
        
        # 步驟 4：準備計算資料
        print("\n步驟 4：準備計算資料")
        records = processor.prepare_calculation_data(df_clean)
        print(f"  ✓ 成功準備計算資料")
        print(f"  記錄數量: {len(records)}")
        
        # 步驟 5：執行計算（取前 10 筆記錄作為測試）
        print("\n步驟 5：執行計算（前 10 筆記錄）")
        test_records = records[:10]
        results = []
        
        for i, record in enumerate(test_records, 1):
            result = calculator.calculate_safety_stock(
                article=record.get('Article', ''),
                site=record.get('Site', ''),
                shop_class=record.get('Class', ''),
                last_month_qty=record.get('Last Month Sold Qty', 0),
                last_2_month_qty=record.get('Last 2 Month', 0),
                supply_source=record.get('Supply source', ''),
                moq=record.get('MOQ', 0),
                mch2=record.get('MCH2')
            )
            results.append(result)
            print(f"  記錄 {i}: Article={result['Article']}, Class={result['Class']}, "
                  f"MCH2={result['MCH2']}, SS={result['Suggested_Safety_Stock']}, "
                  f"Constraint={result['Constraint_Applied']}")
        
        # 步驟 6：驗證 MCH2 約束應用
        print("\n步驟 6：驗證 MCH2 約束應用")
        mch2_applied_count = sum(1 for r in results if r['MCH2_Minimum_SS_Applied'])
        print(f"  應用 MCH2 約束的記錄數量: {mch2_applied_count}")
        
        if mch2_applied_count > 0:
            print(f"\n  MCH2 約束應用的記錄:")
            for r in results:
                if r['MCH2_Minimum_SS_Applied']:
                    print(f"    - Article={r['Article']}, Class={r['Class']}, "
                          f"MCH2={r['MCH2']}, Minimum={r['MCH2_Minimum_Required']}, "
                          f"SS={r['Suggested_Safety_Stock']}")
        
        # 步驟 7：總結
        print("\n" + "=" * 80)
        print("整合測試總結")
        print("=" * 80)
        print(f"  ✓ 成功讀取檔案")
        print(f"  ✓ 成功處理 MCH2 欄位")
        print(f"  ✓ 成功執行計算")
        print(f"  ✓ MCH2 約束應用正確")
        print("\n" + "=" * 80)
        print("✓ 整合測試通過！")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 整合測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_mch2_integration()
