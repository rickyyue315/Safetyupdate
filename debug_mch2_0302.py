# -*- coding: utf-8 -*-
"""
調試腳本：檢查 MCH2 = "0302" 的記錄並驗證約束應用

目標：找出為什麼 MCH2 = 0302 的最低要求沒有被應用
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


def debug_mch2_0302():
    """調試 MCH2 = 0302 的約束應用"""
    
    print("=" * 80)
    print("調試 MCH2 = 0302 的最低要求應用")
    print("=" * 80)
    
    try:
        # 初始化
        settings = Settings()
        processor = DataProcessor()
        calculator = SafetyStockCalculator(settings)
        
        # 步驟 1：讀取並清理資料
        print("\n步驟 1：讀取並清理資料")
        df = processor.load_data("Test_28Jan2026.XLSX")
        df_clean = processor.clean_data(df)
        print(f"  清理後行數: {len(df_clean)}")
        
        # 步驟 2：檢查 MCH2 = "0302" 的記錄
        print("\n步驟 2：檢查 MCH2 欄位")
        if "MCH2" in df_clean.columns:
            print(f"  MCH2 欄位存在 ✓")
            
            # 顯示 MCH2 的唯一值
            mch2_unique = df_clean['MCH2'].unique()
            print(f"\n  MCH2 的唯一值 ({len(mch2_unique)} 個):")
            for val in sorted(mch2_unique):
                count = (df_clean['MCH2'] == val).sum()
                print(f"    - {repr(val)}: {count} 筆")
            
            # 檢查 MCH2 = "0302" 的記錄
            mch2_0302_df = df_clean[df_clean['MCH2'] == "0302"]
            print(f"\n  MCH2 = '0302' 的記錄數量: {len(mch2_0302_df)}")
            
            if len(mch2_0302_df) > 0:
                print(f"\n  前 5 筆 MCH2 = '0302' 的記錄:")
                for idx, row in mch2_0302_df.head(5).iterrows():
                    print(f"    記錄 {idx}:")
                    print(f"      Article: {row.get('Article', 'N/A')}")
                    print(f"      Site: {row.get('Site', 'N/A')}")
                    print(f"      Class: {row.get('Class', 'N/A')}")
                    print(f"      MCH2: {repr(row['MCH2'])}")
                    print(f"      Last Month Sold Qty: {row.get('Last Month Sold Qty', 'N/A')}")
                    print(f"      Last 2 Month: {row.get('Last 2 Month', 'N/A')}")
                    print(f"      MOQ: {row.get('MOQ', 'N/A')}")
                
                # 步驟 3：執行計算並檢查 MCH2 約束應用
                print(f"\n步驟 3：執行計算（前 5 筆 MCH2 = 0302 的記錄）")
                
                for idx, row in mch2_0302_df.head(5).iterrows():
                    result = calculator.calculate_safety_stock(
                        article=row.get('Article', ''),
                        site=row.get('Site', ''),
                        shop_class=row.get('Class', ''),
                        last_month_qty=row.get('Last Month Sold Qty', 0),
                        last_2_month_qty=row.get('Last 2 Month', 0),
                        supply_source=row.get('Supply source', ''),
                        moq=row.get('MOQ', 0),
                        mch2=row.get('MCH2')
                    )
                    
                    print(f"\n  計算結果 {idx}:")
                    print(f"    Article: {result['Article']}")
                    print(f"    Class: {result['Class']}")
                    print(f"    MCH2: {repr(result['MCH2'])}")
                    print(f"    MCH2_Minimum_Required: {result['MCH2_Minimum_Required']}")
                    print(f"    MCH2_Minimum_SS_Applied: {result['MCH2_Minimum_SS_Applied']}")
                    print(f"    Suggested_Safety_Stock: {result['Suggested_Safety_Stock']}")
                    print(f"    Constraint_Applied: {result['Constraint_Applied']}")
            else:
                print(f"  ⚠ 未發現 MCH2 = '0302' 的記錄")
                
                # 顯示數值 302 的分佈
                mch2_302_df = df_clean[df_clean['MCH2'] == "0302"]
                print(f"\n  MCH2 = '0302'（字串）的記錄數量：{len(mch2_302_df)}")
        else:
            print(f"  ✗ MCH2 欄位不存在")
        
        print("\n" + "=" * 80)
        print("調試完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 調試失敗: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_mch2_0302()
