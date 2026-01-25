"""
Settings management module for Safety(Buffer) Stock Calculation
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Settings:
    """管理系統設定參數的類別"""
    
    def __init__(
        self,
        max_safety_stock_days: int = 7,
        moq_multiplier: float = 1.25,
        moq_constraint_mode: str = "multiplier",
        shop_class_max_days: Optional[Dict[str, int]] = None,
        use_target_qty_mode: bool = False
    ):
        """
        初始化設定
        
        參數:
            max_safety_stock_days: 安全庫存天數上限（預設 7，範圍 3-21）
            moq_multiplier: MOQ 約束乘數（預設 1.25）
            moq_constraint_mode: MOQ 約束模式（"multiplier" 或 "add_one"）
            shop_class_max_days: 按 Shop Class 設定的天數上限（可選）
            use_target_qty_mode: 是否使用 Target Qty 模式（預設 False）
        """
        self.max_safety_stock_days = max_safety_stock_days
        self.moq_multiplier = moq_multiplier
        self.moq_constraint_mode = moq_constraint_mode
        self.shop_class_max_days = shop_class_max_days or {}
        self.use_target_qty_mode = use_target_qty_mode
        
        # 驗證設定
        self._validate()
    
    def _validate(self):
        """驗證設定參數是否在有效範圍內"""
        # 驗證 max_safety_stock_days
        if not 3 <= self.max_safety_stock_days <= 21:
            raise ValueError(
                f"max_safety_stock_days 必須在 3-21 之間，當前值：{self.max_safety_stock_days}"
            )
        
        # 驗證 moq_multiplier
        if self.moq_multiplier <= 0:
            raise ValueError(
                f"moq_multiplier 必須大於 0，當前值：{self.moq_multiplier}"
            )
        
        # 驗證 moq_constraint_mode
        if self.moq_constraint_mode not in ["multiplier", "add_one"]:
            raise ValueError(
                f"moq_constraint_mode 必須是 'multiplier' 或 'add_one'，當前值：{self.moq_constraint_mode}"
            )
        
        # 驗證 shop_class_max_days
        valid_shop_classes = ["AA", "A1", "A2", "A3", "B1", "B2", "C1", "C2", "D1"]
        for shop_class, max_days in self.shop_class_max_days.items():
            if shop_class not in valid_shop_classes:
                raise ValueError(
                    f"無效的 Shop Class：{shop_class}，有效值：{valid_shop_classes}"
                )
            if not 3 <= max_days <= 21:
                raise ValueError(
                    f"Shop Class {shop_class} 的 max_days 必須在 3-21 之間，當前值：{max_days}"
                )
    
    def get_max_days_for_shop_class(self, shop_class: str) -> int:
        """
        取得特定 Shop Class 的天數上限
        
        參數:
            shop_class: 店舖等級
            
        返回:
            天數上限（如果未設定則返回全域設定）
        """
        return self.shop_class_max_days.get(shop_class, self.max_safety_stock_days)
    
    def to_dict(self) -> Dict[str, Any]:
        """將設定轉換為字典"""
        return {
            "max_safety_stock_days": self.max_safety_stock_days,
            "moq_multiplier": self.moq_multiplier,
            "moq_constraint_mode": self.moq_constraint_mode,
            "shop_class_max_days": self.shop_class_max_days,
            "use_target_qty_mode": self.use_target_qty_mode
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """從字典建立 Settings 實例"""
        return cls(
            max_safety_stock_days=data.get("max_safety_stock_days", 7),  # type: ignore
            moq_multiplier=data.get("moq_multiplier", 1.25),  # type: ignore
            moq_constraint_mode=data.get("moq_constraint_mode", "multiplier"),  # type: ignore
            shop_class_max_days=data.get("shop_class_max_days", {}),  # type: ignore
            use_target_qty_mode=data.get("use_target_qty_mode", False)  # type: ignore
        )
    
    def save_to_file(self, file_path: str):
        """
        將設定儲存到 JSON 檔案
        
        參數:
            file_path: 檔案路徑
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Settings':
        """
        從 JSON 檔案載入設定
        
        參數:
            file_path: 檔案路徑
            
        返回:
            Settings 實例
        """
        path = Path(file_path)
        
        if not path.exists():
            # 如果檔案不存在，返回預設設定
            return cls()
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        return (
            f"Settings(max_safety_stock_days={self.max_safety_stock_days}, "
            f"moq_multiplier={self.moq_multiplier}, "
            f"moq_constraint_mode='{self.moq_constraint_mode}', "
            f"use_target_qty_mode={self.use_target_qty_mode})"
        )
