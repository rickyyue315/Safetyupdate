"""
Data processing module for Safety(Buffer) Stock Calculation
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from core.constants import (
    REQUIRED_INPUT_FIELDS,
    COLUMN_NAME_ALIASES,
    FIELD_ARTICLE,
    FIELD_SITE,
    FIELD_CLASS,
    FIELD_LAST_MONTH_SOLD_QTY,
    FIELD_LAST_2_MONTH_SOLD_QTY,
    FIELD_SUPPLY_SOURCE,
    FIELD_MOQ,
    FIELD_ORIGINAL_SAFETY_STOCK,
    FIELD_MTD_SOLD_QTY,
    FIELD_PRODUCT_HIERARCHY,
    FIELD_ARTICLE_DESCRIPTION,
    FIELD_RP_TYPE,
    FIELD_TARGET_QTY
)


class DataProcessor:
    """資料處理類別"""
    
    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        標準化欄位名稱
        
        將常見的欄位名稱變體映射到標準名稱
        
        參數:
            df: 原始 DataFrame
            
        返回:
            欄位名稱標準化後的 DataFrame
        """
        # 建立副本以避免修改原始資料
        df_normalized = df.copy()
        
        # 建立欄位名稱映射
        column_mapping = {}
        for col in df_normalized.columns:
            # 檢查是否為別名
            if col in COLUMN_NAME_ALIASES:
                column_mapping[col] = COLUMN_NAME_ALIASES[col]
            # 檢查是否為大小寫變體（忽略大小寫比較）
            elif col.lower() in [k.lower() for k in COLUMN_NAME_ALIASES.keys()]:
                # 找到對應的標準名稱
                for alias, standard in COLUMN_NAME_ALIASES.items():
                    if col.lower() == alias.lower():
                        column_mapping[col] = standard
                        break
        
        # 應用欄位名稱映射
        if column_mapping:
            df_normalized = df_normalized.rename(columns=column_mapping)
        
        return df_normalized
    
    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """
        載入 CSV 或 Excel 檔案
        
        自動偵測檔案格式並使用適當的 pandas 方法載入，
        並自動標準化欄位名稱
        
        參數:
            file_path: 檔案路徑
            
        返回:
            包含資料的 DataFrame（欄位名稱已標準化）
            
        異常:
            ValueError: 當檔案格式不支援時
            FileNotFoundError: 當檔案不存在時
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"檔案不存在：{file_path}")
        
        file_ext = path.suffix.lower()
        
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(
                f"不支援的檔案格式：{file_ext}，"
                f"請使用 .csv、.xlsx 或 .xls 格式"
            )
        
        # 自動標準化欄位名稱
        df = DataProcessor.normalize_column_names(df)
        
        return df
    
    @staticmethod
    def validate_required_columns(df: pd.DataFrame) -> bool:
        """
        驗證資料是否包含所有必要欄位
        
        必要欄位：
        - Article
        - Site
        - Class
        - Last Month Sold Qty
        - Last 2 Month Sold Qty
        - Supply Source
        - MOQ
        
        參數:
            df: 資料 DataFrame
            
        返回:
            True 如果所有必要欄位都存在，否則 False
        """
        missing_columns = [
            col for col in REQUIRED_INPUT_FIELDS 
            if col not in df.columns
        ]
        
        if missing_columns:
            return False
        
        return True
    
    @staticmethod
    def get_missing_columns(df: pd.DataFrame) -> List[str]:
        """
        取得缺失的必要欄位列表
        
        參數:
            df: 資料 DataFrame
            
        返回:
            缺失的欄位名稱列表
        """
        missing_columns = [
            col for col in REQUIRED_INPUT_FIELDS 
            if col not in df.columns
        ]
        return missing_columns
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗資料
        
        執行以下操作：
        - 移除空值
        - 轉換資料類型
        - 處理異常值
        
        參數:
            df: 原始資料 DataFrame
            
        返回:
            清洗後的 DataFrame
        """
        # 建立副本以避免修改原始資料
        df_clean = df.copy()
        
        # 移除包含空值的列
        df_clean = df_clean.dropna(subset=REQUIRED_INPUT_FIELDS)
        
        # 轉換數值欄位
        numeric_columns = [
            FIELD_LAST_MONTH_SOLD_QTY,
            FIELD_LAST_2_MONTH_SOLD_QTY,
            FIELD_MOQ
        ]
        
        # 新增可選欄位（如果存在）
        optional_numeric_columns = []
        if FIELD_ORIGINAL_SAFETY_STOCK in df_clean.columns:
            optional_numeric_columns.append(FIELD_ORIGINAL_SAFETY_STOCK)
        if FIELD_MTD_SOLD_QTY in df_clean.columns:
            optional_numeric_columns.append(FIELD_MTD_SOLD_QTY)
        if FIELD_TARGET_QTY in df_clean.columns:
            optional_numeric_columns.append(FIELD_TARGET_QTY)
        
        all_numeric_columns = numeric_columns + optional_numeric_columns
        
        for col in all_numeric_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 移除轉換後仍為 NaN 的列（只檢查必要欄位）
        df_clean = df_clean.dropna(subset=numeric_columns)
        
        # 確保數值欄位為非負數
        for col in all_numeric_columns:
            df_clean[col] = df_clean[col].clip(lower=0)
        
        # 轉換 Supply Source 為字串
        df_clean[FIELD_SUPPLY_SOURCE] = df_clean[FIELD_SUPPLY_SOURCE].astype(str)
        
        # 轉換 Shop Class 為大寫
        df_clean[FIELD_CLASS] = df_clean[FIELD_CLASS].astype(str).str.upper()
        
        return df_clean
    
    @staticmethod
    def prepare_calculation_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        將 DataFrame 轉換為計算所需的格式
        
        返回字典列表，每個字典代表一筆記錄
        
        參數:
            df: 清洗後的 DataFrame
            
        返回:
            字典列表
        """
        # 準備欄位列表（包含必要欄位和可選欄位）
        columns_to_include = REQUIRED_INPUT_FIELDS.copy()
        
        # 新增可選欄位（如果存在）
        # 使用原始欄位名稱（從 df.columns 中獲取）以確保與輸入檔案一致
        if FIELD_ORIGINAL_SAFETY_STOCK in df.columns:
            columns_to_include.append(FIELD_ORIGINAL_SAFETY_STOCK)
        if FIELD_MTD_SOLD_QTY in df.columns:
            columns_to_include.append(FIELD_MTD_SOLD_QTY)
        if FIELD_TARGET_QTY in df.columns:
            columns_to_include.append(FIELD_TARGET_QTY)
        # 新增 Product Hierarchy 和 Article Description（如果存在）
        if FIELD_PRODUCT_HIERARCHY in df.columns:
            columns_to_include.append(FIELD_PRODUCT_HIERARCHY)
        if FIELD_ARTICLE_DESCRIPTION in df.columns:
            columns_to_include.append(FIELD_ARTICLE_DESCRIPTION)
        # 新增 RP Type（如果存在）
        if FIELD_RP_TYPE in df.columns:
            columns_to_include.append(FIELD_RP_TYPE)
        
        records = df[columns_to_include].to_dict('records')
        return records
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        取得資料摘要統計
        
        參數:
            df: 資料 DataFrame
            
        返回:
            包含摘要統計的字典
        """
        summary = {
            "total_records": len(df),
            "unique_articles": df[FIELD_ARTICLE].nunique(),
            "unique_sites": df[FIELD_SITE].nunique(),
            "unique_classes": df[FIELD_CLASS].nunique(),
            "shop_class_distribution": df[FIELD_CLASS].value_counts().to_dict(),
            "supply_source_distribution": df[FIELD_SUPPLY_SOURCE].value_counts().to_dict()
        }
        return summary
