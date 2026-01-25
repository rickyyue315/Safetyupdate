"""
Constants definition module for Safety(Buffer) Stock Calculation
"""
from typing import Dict


# MF（合併因素）對照表
# 依 Shop Class 定義不同的合併因素和服務水準
MF_TABLE: Dict[str, Dict[str, float]] = {
    "AA": {"value": 2.58, "service_level": 99.5},
    "A1": {"value": 2.33, "service_level": 99.0},
    "A2": {"value": 2.05, "service_level": 98.0},
    "A3": {"value": 1.88, "service_level": 97.0},
    "B1": {"value": 1.75, "service_level": 96.0},
    "B2": {"value": 1.645, "service_level": 95.0},
    "C1": {"value": 1.555, "service_level": 94.0},
    "C2": {"value": 1.48, "service_level": 93.0},
    "D1": {"value": 1.28, "service_level": 90.0}
}


# Supply Source 對應的前置時間表（天數）
# "1" 或 "4" → 7 天（行貨）
# "2" → 3 天（倉貨）
# 其他 → 預設 7 天
LEAD_TIME_MAP: Dict[str, int] = {
    "1": 7,  # 行貨
    "2": 3,  # 倉貨
    "4": 7   # 行貨
}
DEFAULT_LEAD_TIME = 7


# 安全庫存天數上限範圍
MIN_MAX_DAYS = 7
MAX_MAX_DAYS = 14


# MOQ 約束模式
MOQ_MODE_MULTIPLIER = "multiplier"
MOQ_MODE_ADD_ONE = "add_one"


# 資料欄位名稱
FIELD_ARTICLE = "Article"
FIELD_SITE = "Site"
FIELD_CLASS = "Class"
FIELD_LAST_MONTH_SOLD_QTY = "Last Month Sold Qty"
FIELD_LAST_2_MONTH_SOLD_QTY = "Last 2 Month Sold Qty"
FIELD_SUPPLY_SOURCE = "Supply Source"
FIELD_MOQ = "MOQ"

# 原始輸入欄位（可選）
FIELD_ORIGINAL_SAFETY_STOCK = "Original_Safety_Stock"
FIELD_MTD_SOLD_QTY = "MTD_Sold_Qty"
FIELD_PRODUCT_HIERARCHY = "Product Hierarchy"
FIELD_ARTICLE_DESCRIPTION = "Article Description"
FIELD_RP_TYPE = "RP Type"
FIELD_TARGET_QTY = "Target Qty"


# 輸出欄位名稱
FIELD_AVG_DAILY_SALES = "Avg_Daily_Sales"
FIELD_LEAD_TIME_DAYS = "Lead_Time_Days"
FIELD_MF_USED = "MF_Used"
FIELD_MF_SERVICE_LEVEL = "MF_Service_Level"
FIELD_PRELIMINARY_SS = "Preliminary_SS"
FIELD_SS_AFTER_MOQ = "SS_after_MOQ"
FIELD_USER_MAX_DAYS_APPLIED = "User_Max_Days_Applied"
FIELD_SUGGESTED_SAFETY_STOCK = "Suggested_Safety_Stock"
FIELD_CONSTRAINT_APPLIED = "Constraint_Applied"
FIELD_SAFETY_STOCK_DAYS = "Safety_Stock_Days"
FIELD_ORIGINAL_SAFETY_STOCK_DAYS = "Original_Safety_Stock_Days"


# 約束類型
CONSTRAINT_NONE = "無"
CONSTRAINT_MOQ = "MOQ"
CONSTRAINT_MAX_DAYS = "天數上限"
CONSTRAINT_BOTH = "兩者"


# 有效的 Shop Class 列表
VALID_SHOP_CLASSES = [
    "AA", "A1", "A2", "A3", "B1", "B2", "C1", "C2", "D1"
]


# 必要的輸入欄位
REQUIRED_INPUT_FIELDS = [
    FIELD_ARTICLE,
    FIELD_SITE,
    FIELD_CLASS,
    FIELD_LAST_MONTH_SOLD_QTY,
    FIELD_LAST_2_MONTH_SOLD_QTY,
    FIELD_SUPPLY_SOURCE,
    FIELD_MOQ
]


# 欄位名稱映射表（用於處理不同的欄位名稱變體）
# 將常見的欄位名稱變體映射到標準名稱
COLUMN_NAME_ALIASES: Dict[str, str] = {
    # Supply Source 的變體
    "Supply source": FIELD_SUPPLY_SOURCE,
    "supply source": FIELD_SUPPLY_SOURCE,
    "supply Source": FIELD_SUPPLY_SOURCE,
    
    # Safety Stock 的變體
    "Safety Stock": FIELD_ORIGINAL_SAFETY_STOCK,
    "Safety stock": FIELD_ORIGINAL_SAFETY_STOCK,
    "safety stock": FIELD_ORIGINAL_SAFETY_STOCK,
    
    # MTD Sold Qty 的變體
    "MTD Sold Qty": FIELD_MTD_SOLD_QTY,
    "MTD sold qty": FIELD_MTD_SOLD_QTY,
    "mtd sold qty": FIELD_MTD_SOLD_QTY,
    
    # Last Month Sold Qty 的變體
    "Last Month Sold Qty": FIELD_LAST_MONTH_SOLD_QTY,
    "Last month sold qty": FIELD_LAST_MONTH_SOLD_QTY,
    "last month sold qty": FIELD_LAST_MONTH_SOLD_QTY,
    
    # Last 2 Month Sold Qty 的變體
    "Last 2 Month": FIELD_LAST_2_MONTH_SOLD_QTY,
    "Last 2 Month Sold Qty": FIELD_LAST_2_MONTH_SOLD_QTY,
    "last 2 month": FIELD_LAST_2_MONTH_SOLD_QTY,
    "Last 2 month": FIELD_LAST_2_MONTH_SOLD_QTY,
    "last 2 Month": FIELD_LAST_2_MONTH_SOLD_QTY,
    
    # Product Hierarchy 的變體
    "Product Hierarchy": FIELD_PRODUCT_HIERARCHY,
    "Product hierarchy": FIELD_PRODUCT_HIERARCHY,
    "product hierarchy": FIELD_PRODUCT_HIERARCHY,
    
    # Article Description 的變體
    "Article Description": FIELD_ARTICLE_DESCRIPTION,
    "Article description": FIELD_ARTICLE_DESCRIPTION,
    "article description": FIELD_ARTICLE_DESCRIPTION,

    # RP Type 的變體
    "RP Type": FIELD_RP_TYPE,
    "RP type": FIELD_RP_TYPE,
    "rp type": FIELD_RP_TYPE,
    
    # Class 的變體
    "class": FIELD_CLASS,
    "CLASS": FIELD_CLASS,
    "Shop Class": FIELD_CLASS,
    "shop class": FIELD_CLASS,
    "Shop class": FIELD_CLASS,
    
    # Target Qty 的變體
    "Target Qty": FIELD_TARGET_QTY,
    "Target qty": FIELD_TARGET_QTY,
    "target qty": FIELD_TARGET_QTY,
    "Target Quantity": FIELD_TARGET_QTY,
    "Target quantity": FIELD_TARGET_QTY,
    "target quantity": FIELD_TARGET_QTY,
}
