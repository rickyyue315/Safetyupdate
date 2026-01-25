"""
Data validation module for Safety(Buffer) Stock Calculation
"""
from typing import Tuple, Any, Dict
from config.settings import Settings
from core.constants import (
    VALID_SHOP_CLASSES,
    MIN_MAX_DAYS,
    MAX_MAX_DAYS,
    MOQ_MODE_MULTIPLIER,
    MOQ_MODE_ADD_ONE
)


def validate_numeric_value(
    value: Any,
    field_name: str,
    min_value: float = 0,
    allow_zero: bool = True
) -> Tuple[bool, str]:
    """
    驗證數值欄位是否有效
    
    參數:
        value: 要驗證的值
        field_name: 欄位名稱（用於錯誤訊息）
        min_value: 最小允許值（預設 0）
        allow_zero: 是否允許零值（預設 True）
        
    返回:
        (is_valid, error_message)
    """
    try:
        num_value = float(value)
    except (TypeError, ValueError):
        return False, f"{field_name} 必須是數值"
    
    if not allow_zero and num_value == 0:
        return False, f"{field_name} 不能為零"
    
    if num_value < min_value:
        return False, f"{field_name} 必須大於或等於 {min_value}"
    
    return True, ""


def validate_shop_class(shop_class: str) -> Tuple[bool, str]:
    """
    驗證 Shop Class 是否在有效範圍內
    
    有效值：AA, A1, A2, A3, B1, B2, C1, C2, D1
    
    參數:
        shop_class: 店舖等級
        
    返回:
        (is_valid, error_message)
    """
    if not shop_class:
        return False, "Shop Class 不能為空"
    
    shop_class_upper = shop_class.upper()
    
    if shop_class_upper not in VALID_SHOP_CLASSES:
        return False, (
            f"無效的 Shop Class：{shop_class}，"
            f"有效值：{', '.join(VALID_SHOP_CLASSES)}"
        )
    
    return True, ""


def validate_supply_source(supply_source: str) -> Tuple[bool, str]:
    """
    驗證 Supply Source 格式
    
    參數:
        supply_source: 供應來源代碼
        
    返回:
        (is_valid, error_message)
    """
    if not supply_source:
        return False, "Supply Source 不能為空"
    
    # Supply Source 可以是任何非空字串，系統會使用預設值處理未知值
    # 所以這裡只做基本驗證
    return True, ""


def validate_settings(settings: Settings) -> Tuple[bool, str]:
    """
    驗證使用者設定是否在有效範圍內
    
    - max_safety_stock_days: 7-14
    - moq_multiplier: > 0
    - moq_constraint_mode: "multiplier" 或 "add_one"
    
    參數:
        settings: 設定物件
        
    返回:
        (is_valid, error_message)
    """
    # 驗證 max_safety_stock_days
    if not MIN_MAX_DAYS <= settings.max_safety_stock_days <= MAX_MAX_DAYS:
        return False, (
            f"max_safety_stock_days 必須在 {MIN_MAX_DAYS}-{MAX_MAX_DAYS} 之間，"
            f"當前值：{settings.max_safety_stock_days}"
        )
    
    # 驗證 moq_multiplier
    if settings.moq_multiplier <= 0:
        return False, (
            f"moq_multiplier 必須大於 0，"
            f"當前值：{settings.moq_multiplier}"
        )
    
    # 驗證 moq_constraint_mode
    if settings.moq_constraint_mode not in [MOQ_MODE_MULTIPLIER, MOQ_MODE_ADD_ONE]:
        return False, (
            f"moq_constraint_mode 必須是 '{MOQ_MODE_MULTIPLIER}' "
            f"或 '{MOQ_MODE_ADD_ONE}'，當前值：{settings.moq_constraint_mode}"
        )
    
    # 驗證 shop_class_max_days
    valid_shop_classes = ["AA", "A1", "A2", "A3", "B1", "B2", "C1", "C2", "D1"]
    for shop_class, max_days in settings.shop_class_max_days.items():
        if shop_class not in valid_shop_classes:
            return False, (
                f"無效的 Shop Class：{shop_class}，"
                f"有效值：{valid_shop_classes}"
            )
        if not MIN_MAX_DAYS <= max_days <= MAX_MAX_DAYS:
            return False, (
                f"Shop Class {shop_class} 的 max_days 必須在 "
                f"{MIN_MAX_DAYS}-{MAX_MAX_DAYS} 之間，當前值：{max_days}"
            )
    
    return True, ""


def validate_record(record: Dict[str, Any]) -> Tuple[bool, str]:
    """
    驗證單筆資料記錄
    
    參數:
        record: 資料記錄字典
        
    返回:
        (is_valid, error_message)
    """
    # 驗證 Article
    if "Article" not in record or not record["Article"]:
        return False, "Article 不能為空"
    
    # 驗證 Site
    if "Site" not in record or not record["Site"]:
        return False, "Site 不能為空"
    
    # 驗證 Class
    is_valid, error_msg = validate_shop_class(record.get("Class", ""))
    if not is_valid:
        return False, error_msg
    
    # 驗證 Last Month Sold Qty
    is_valid, error_msg = validate_numeric_value(
        record.get("Last Month Sold Qty", 0),
        "Last Month Sold Qty",
        min_value=0,
        allow_zero=True
    )
    if not is_valid:
        return False, error_msg
    
    # 驗證 Last 2 Month Sold Qty
    is_valid, error_msg = validate_numeric_value(
        record.get("Last 2 Month Sold Qty", 0),
        "Last 2 Month Sold Qty",
        min_value=0,
        allow_zero=True
    )
    if not is_valid:
        return False, error_msg
    
    # 驗證 Supply Source
    is_valid, error_msg = validate_supply_source(
        str(record.get("Supply Source", ""))
    )
    if not is_valid:
        return False, error_msg
    
    # 驗證 MOQ
    is_valid, error_msg = validate_numeric_value(
        record.get("MOQ", 0),
        "MOQ",
        min_value=0,
        allow_zero=False
    )
    if not is_valid:
        return False, error_msg
    
    return True, ""
