"""
Export functions for Safety(Buffer) Stock Calculation
"""
import pandas as pd
from pathlib import Path


def export_to_excel(df: pd.DataFrame, output_path: str) -> bool:
    """
    將計算結果匯出為 Excel 檔案
    
    參數:
        df: 要匯出的 DataFrame
        output_path: 輸出檔案路徑
        
    返回:
        bool: 匯出是否成功
    """
    try:
        # 檢查資料是否有效
        if df is None or len(df) == 0:
            raise ValueError("DataFrame 為空或無效")
        
        # 確保輸出目錄存在
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 匯出為 Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 結果工作表 - 調整欄位順序
            display_columns = [
                'Article', 'Site', 'Class',
                'Product Hierarchy',      # 新增
                'Article Description',       # 新增
                'Original_Safety_Stock',  # 新增
                'Original_Safety_Stock_Days',  # 新增
                'MTD_Sold_Qty',            # 新增
                'Last_Month_Sold_Qty',     # 新增
                'Last_2_Month_Sold_Qty',   # 新增
                'Avg_Daily_Sales',
                'Lead_Time_Days',
                'MF_Used', 'MF_Service_Level',
                'Preliminary_SS', 'SS_after_MOQ',
                'User_Max_Days_Applied',
                'Suggested_Safety_Stock',
                'Suggested_Diff',          # 新增
                'Constraint_Applied',
                'Safety_Stock_Days',
                'Preliminary_SS_Days',      # 新增
                'SS_after_MOQ_Days',        # 新增
                'Suggested_SS_Days',        # 新增
                'Target_Safety_Stock',      # 新增
                'Target_Diff',             # 新增
                'Target_Safety_Stock_Days',  # 新增
                'Target_Qty_Used',         # 新增
                'Calculation_Mode',          # 新增
                'Notes'                    # 新增
            ]
            # 只輸出存在的欄位
            existing_columns = [col for col in display_columns if col in df.columns]
            
            # 確保 Article 欄位以文字格式輸出
            df_copy = df.copy()
            if 'Article' in df_copy.columns:
                df_copy['Article'] = df_copy['Article'].astype(str)
            
            df_copy.to_excel(writer, sheet_name='Results', index=False, columns=existing_columns)
            
            # 統計摘要工作表 - 全體統計
            summary_data = {
                "項目": [
                    "總記錄數",
                    "觸發 MOQ 約束記錄數",
                    "觸發天數上限記錄數",
                    "平均支撐天數"
                ],
                "數值": [
                    len(df),
                    (df['Constraint_Applied'] == 'MOQ').sum(),
                    (df['Constraint_Applied'] == '天數上限').sum(),
                    df['Safety_Stock_Days'].mean()
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False, startrow=0)
            
            # 新增按 SKU 分類的統計
            if 'Article' in df.columns:
                sku_summary = df.groupby('Article').agg({
                    'Site': 'count',
                    'Product Hierarchy': 'first',
                    'Article Description': 'first',
                    'Original_Safety_Stock': 'sum',
                    'MTD_Sold_Qty': 'sum',
                    'Last_Month_Sold_Qty': 'sum',
                    'Last_2_Month_Sold_Qty': 'sum',
                    'Suggested_Safety_Stock': 'sum',
                    'Safety_Stock_Days': 'mean'
                }).reset_index()
                
                # 重新命名欄位
                sku_summary.columns = [
                    'SKU (Article)',
                    '門市數量',
                    '產品階層',
                    '商品描述',
                    '原始安全庫存總和',
                    'MTD銷量總和',
                    '上月銷量總和',
                    '前兩月銷量總和',
                    '建議安全庫存總和',
                    '平均支撐天數'
                ]
                
                # 寫入 SKU 摘要到 Summary 工作表（從第 6 行開始）
                sku_summary.to_excel(writer, sheet_name='Summary', index=False, startrow=len(summary_df) + 2)
        
        return True
        
    except ValueError as e:
        raise ValueError(f"資料驗證失敗: {str(e)}")
    except PermissionError:
        raise PermissionError(f"沒有權限寫入檔案: {output_path}")
    except Exception as e:
        raise Exception(f"匯出 Excel 時發生錯誤: {str(e)}")


def export_to_csv(df: pd.DataFrame, output_path: str) -> bool:
    """
    將計算結果匯出為 CSV 檔案
    
    參數:
        df: 要匯出的 DataFrame
        output_path: 輸出檔案路徑
        
    返回:
        bool: 匯出是否成功
    """
    try:
        # 檢查資料是否有效
        if df is None or len(df) == 0:
            raise ValueError("DataFrame 為空或無效")
        
        # 確保輸出目錄存在
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 匯出為 CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return True
        
    except ValueError as e:
        raise ValueError(f"資料驗證失敗: {str(e)}")
    except PermissionError:
        raise PermissionError(f"沒有權限寫入檔案: {output_path}")
    except Exception as e:
        raise Exception(f"匯出 CSV 時發生錯誤: {str(e)}")
