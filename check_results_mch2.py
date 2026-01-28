# -*- coding: utf-8 -*-
"""
檢查結果檔案中的 MCH2 欄位
"""

import sys
import io
import pandas as pd

# 設定標準輸出為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("檢查結果檔案中的 MCH2 欄位")
print("=" * 80)

try:
    # 讀取結果檔案
    df = pd.read_excel("safety_stock_results_20260128_123222.xlsx")
    
    print(f"\n檔案信息：")
    print(f"  總列數: {len(df.columns)}")
    print(f"  總行數: {len(df)}")
    
    print(f"\n所有欄位名稱:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # 檢查 MCH2 相關欄位
    mch2_columns = [col for col in df.columns if 'MCH2' in col.upper()]
    print(f"\n包含 'MCH2' 的欄位: {mch2_columns}")
    
    if not mch2_columns:
        print(f"  ⚠ 結果檔案中沒有 MCH2 相關欄位")
        print(f"\n這可能表示：")
        print(f"  1. 結果檔案是使用舊版本生成的（v2.2 或更早）")
        print(f"  2. 需要重新執行應用程式以生成包含 MCH2 欄位的結果")
    else:
        print(f"\n  ✓ 發現 MCH2 相關欄位")
        
        # 顯示 MCH2 欄位的內容（前 10 行）
        for col in mch2_columns:
            print(f"\n  {col} 欄位（前 10 行）:")
            print(f"    {df[col].head(10).tolist()}")
            
            # 檢查 MCH2 = "0302" 的記錄
            if '0302' in df[col].astype(str).unique() or 302 in df[col].unique():
                mch2_0302_count = ((df[col].astype(str) == '0302') | (df[col] == 302)).sum()
                print(f"    MCH2 = '0302' 或 302 的記錄數量: {mch2_0302_count}")
    
    print("\n" + "=" * 80)
    
except FileNotFoundError:
    print(f"\n✗ 找不到檔案: safety_stock_results_20260128_123222.xlsx")
except Exception as e:
    print(f"\n✗ 讀取檔案失敗: {str(e)}")
    import traceback
    traceback.print_exc()
