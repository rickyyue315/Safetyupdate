# -*- coding: utf-8 -*-
"""
詳細檢查結果檔案中 MCH2 = 0302 的記錄
"""

import sys
import io
import pandas as pd

# 設定標準輸出為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("詳細檢查結果檔案中 MCH2 = 0302 的記錄")
print("=" * 80)

try:
    # 讀取結果檔案
    df = pd.read_excel("safety_stock_results_20260128_123222.xlsx")
    
    # 檢查 MCH2 = "0302" 或 302 的記錄
    mch2_0302_df = df[(df['MCH2'].astype(str) == '0302') | (df['MCH2'] == 302)]
    print(f"\nMCH2 = '0302' 或 302 的記錄數量: {len(mch2_0302_df)}")
    
    if len(mch2_0302_df) > 0:
        print(f"\n前 5 筆記錄的詳細信息：")
        for idx, (i, row) in enumerate(mch2_0302_df.head(5).iterrows(), 1):
            print(f"\n  記錄 {idx}:")
            print(f"    Article: {row['Article']}")
            print(f"    Site: {row['Site']}")
            print(f"    Class: {row['Class']}")
            print(f"    MCH2: {row['MCH2']}")
            print(f"    Suggested_Safety_Stock: {row['Suggested_Safety_Stock']}")
            print(f"    MCH2_Minimum_Required: {row['MCH2_Minimum_Required']}")
            print(f"    MCH2_Minimum_SS_Applied: {row['MCH2_Minimum_SS_Applied']}")
            print(f"    Constraint_Applied: {row['Constraint_Applied']}")
            print(f"    Last_Month_Sold_Qty: {row['Last_Month_Sold_Qty']}")
            print(f"    Last_2_Month_Sold_Qty: {row['Last_2_Month_Sold_Qty']}")
        
        # 統計 MCH2_Minimum_SS_Applied = True 的記錄
        applied_count = (mch2_0302_df['MCH2_Minimum_SS_Applied'] == True).sum()
        print(f"\n\n  MCH2 = 0302 的記錄中，MCH2_Minimum_SS_Applied = True 的記錄數量: {applied_count}")
        
        if applied_count > 0:
            print(f"\n  應用了 MCH2 約束的記錄:")
            for idx, (i, row) in enumerate(mch2_0302_df[mch2_0302_df['MCH2_Minimum_SS_Applied'] == True].head(5).iterrows(), 1):
                print(f"    {idx}. Article={row['Article']}, Class={row['Class']}, SS={row['Suggested_Safety_Stock']}, Min={row['MCH2_Minimum_Required']}")
        else:
            print(f"\n  ⚠ 沒有應用 MCH2 約束")
            print(f"  這表示結果檔案可能是使用舊版本計算生成的")
    
    print("\n" + "=" * 80)
    
except FileNotFoundError:
    print(f"\n✗ 找不到檔案: safety_stock_results_20260128_123222.xlsx")
except Exception as e:
    print(f"\n✗ 讀取檔案失敗: {str(e)}")
    import traceback
    traceback.print_exc()
