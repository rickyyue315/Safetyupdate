# -*- coding: utf-8 -*-
"""
驗證 Test_28Jan2026.XLSX 檔案中的 MCH2 欄位
"""

import pandas as pd
import sys
import io

# 設定標準輸出為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verify_mch2_field():
    """驗證 MCH2 欄位是否存在並檢查其內容"""
    
    print("=" * 80)
    print("驗證 Test_28Jan2026.XLSX 檔案中的 MCH2 欄位")
    print("=" * 80)
    
    try:
        # 讀取 Excel 檔案
        df = pd.read_excel("Test_28Jan2026.XLSX")
        
        print(f"\n✓ 成功讀取檔案")
        print(f"  總行數: {len(df)}")
        print(f"  總欄位數: {len(df.columns)}")
        
        # 顯示所有欄位名稱
        print(f"\n所有欄位名稱:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        # 檢查 MCH2 欄位是否存在
        if "MCH2" in df.columns:
            print(f"\n✓ MCH2 欄位存在")
            
            # 顯示 MCH2 欄位的統計資訊
            print(f"\nMCH2 欄位統計:")
            print(f"  非空值數量: {df['MCH2'].notna().sum()}")
            print(f"  空值數量: {df['MCH2'].isna().sum()}")
            print(f"  唯一值數量: {df['MCH2'].nunique()}")
            
            # 顯示 MCH2 的唯一值及其計數
            print(f"\nMCH2 唯一值分佈:")
            mch2_counts = df['MCH2'].value_counts(dropna=False)
            for value, count in mch2_counts.items():
                if pd.isna(value):
                    print(f"  NaN (空值): {count} 筆")
                else:
                    print(f"  {value}: {count} 筆")
            
            # 檢查是否有 "0302" 值
            if "0302" in df['MCH2'].values:
                print(f"\n✓ 發現 MCH2 = '0302' 的記錄")
                mch2_0302_count = (df['MCH2'] == "0302").sum()
                print(f"  數量: {mch2_0302_count} 筆")
                
                # 顯示前 5 筆 MCH2 = 0302 的記錄
                print(f"\n前 5 筆 MCH2 = '0302' 的記錄:")
                mch2_0302_records = df[df['MCH2'] == "0302"].head(5)
                for idx, row in mch2_0302_records.iterrows():
                    print(f"  記錄 {idx + 1}:")
                    print(f"    Article: {row.get('Article', 'N/A')}")
                    print(f"    Site: {row.get('Site', 'N/A')}")
                    print(f"    Class: {row.get('Class', 'N/A')}")
                    print(f"    MCH2: {row['MCH2']}")
            else:
                print(f"\n⚠ 未發現 MCH2 = '0302' 的記錄")
            
            # 檢查 Class 欄位是否存在
            if "Class" in df.columns:
                print(f"\n✓ Class 欄位存在")
                
                # 顯示 Class 的唯一值
                print(f"\nClass 唯一值分佈:")
                class_counts = df['Class'].value_counts()
                for class_value, count in class_counts.items():
                    print(f"  {class_value}: {count} 筆")
                
                # 檢查 MCH2 = 0302 的記錄中各 Class 的分佈
                if "0302" in df['MCH2'].values:
                    print(f"\nMCH2 = '0302' 的記錄中 Class 分佈:")
                    mch2_0302_df = df[df['MCH2'] == "0302"]
                    class_distribution = mch2_0302_df['Class'].value_counts()
                    for class_value, count in class_distribution.items():
                        print(f"  {class_value}: {count} 筆")
            else:
                print(f"\n⚠ Class 欄位不存在")
            
        else:
            print(f"\n✗ MCH2 欄位不存在")
            print(f"  請確認檔案是否包含 MCH2 欄位")
            
            # 建議可能的欄位名稱
            similar_columns = [col for col in df.columns if 'mch' in col.lower()]
            if similar_columns:
                print(f"\n  發現類似欄位: {similar_columns}")
        
        print("\n" + "=" * 80)
        print("驗證完成")
        print("=" * 80)
        
        return True
        
    except FileNotFoundError:
        print(f"\n✗ 檔案不存在: Test_28Jan2026.XLSX")
        print(f"  請確認檔案路徑正確")
        return False
    except Exception as e:
        print(f"\n✗ 讀取檔案時發生錯誤: {str(e)}")
        return False


if __name__ == "__main__":
    verify_mch2_field()
