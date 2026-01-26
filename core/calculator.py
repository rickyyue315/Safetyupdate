"""
Core calculation module for Safety(Buffer) Stock Calculation
"""
import math
from typing import Dict, Any, Tuple, Optional
from config.settings import Settings
from core.constants import (
    MF_TABLE,
    LEAD_TIME_MAP,
    DEFAULT_LEAD_TIME,
    MOQ_MODE_MULTIPLIER,
    MOQ_MODE_ADD_ONE,
    CONSTRAINT_NONE,
    CONSTRAINT_MOQ,
    CONSTRAINT_MAX_DAYS,
    CONSTRAINT_BOTH,
    FIELD_AVG_DAILY_SALES,
    FIELD_LEAD_TIME_DAYS,
    FIELD_MF_USED,
    FIELD_MF_SERVICE_LEVEL,
    FIELD_PRELIMINARY_SS,
    FIELD_SS_AFTER_MOQ,
    FIELD_USER_MAX_DAYS_APPLIED,
    FIELD_SUGGESTED_SAFETY_STOCK,
    FIELD_CONSTRAINT_APPLIED,
    FIELD_SAFETY_STOCK_DAYS,
    FIELD_ORIGINAL_SAFETY_STOCK_DAYS,
    FIELD_ORIGINAL_SAFETY_STOCK,
    FIELD_MTD_SOLD_QTY,
    FIELD_PRODUCT_HIERARCHY,
    FIELD_ARTICLE_DESCRIPTION,
    FIELD_RP_TYPE,
    FIELD_TARGET_QTY,
    FIELD_TARGET_SAFETY_STOCK,
    FIELD_TARGET_SAFETY_STOCK_DAYS
)


class SafetyStockCalculator:
    """安全庫存計算核心類別"""
    
    def __init__(self, settings: Settings):
        """
        初始化計算器
        
        參數:
            settings: 系統設定
        """
        self.settings = settings
    
    def calculate_avg_daily_sales(
        self,
        last_month_qty: float,
        last_2_month_qty: float
    ) -> float:
        """
        計算平均日銷量，保留 2 位小數
        
        公式：Avg_Daily_Sales = (Last Month Sold Qty + Last 2 Month Sold Qty) / 60
        
        參數:
            last_month_qty: 上個月銷量
            last_2_month_qty: 前兩個月銷量總和
            
        返回:
            平均日銷量（保留 2 位小數）
        """
        avg_daily_sales = (last_month_qty + last_2_month_qty) / 60
        return round(avg_daily_sales, 2)
    
    def determine_lead_time(self, supply_source: str) -> int:
        """
        依 Supply Source 判斷前置時間
        
        - "1" 或 "4" → 7 天（行貨）
        - "2" → 3 天（倉貨）
        - 其他 → 預設 7 天
        
        參數:
            supply_source: 供應來源代碼
            
        返回:
            前置時間（天數）
        """
        return LEAD_TIME_MAP.get(str(supply_source), DEFAULT_LEAD_TIME)
    
    def get_merge_factor(self, shop_class: str) -> Dict[str, float]:
        """
        依 Shop Class 取得合併因素 MF
        
        參數:
            shop_class: 店舖等級
            
        返回:
            包含 value 和 service_level 的字典
            
        異常:
            ValueError: 當 Shop Class 無效時
        """
        shop_class = shop_class.upper()
        if shop_class not in MF_TABLE:
            raise ValueError(
                f"無效的 Shop Class：{shop_class}，有效值：{list(MF_TABLE.keys())}"
            )
        return MF_TABLE[shop_class]
    
    def calculate_preliminary_ss(
        self,
        avg_daily_sales: float,
        lead_time: int,
        mf: float
    ) -> float:
        """
        計算初步安全庫存
        
        公式：SS_preliminary = Avg_Daily_Sales × √Lead_Time_Days × MF
        
        參數:
            avg_daily_sales: 平均日銷量
            lead_time: 前置時間（天數）
            mf: 合併因素
            
        返回:
            初步安全庫存（向上取整為整數）
        """
        preliminary_ss = avg_daily_sales * math.sqrt(lead_time) * mf
        return math.ceil(preliminary_ss)
    
    def apply_moq_constraint(
        self,
        preliminary_ss: float,
        moq: float,
        multiplier: float,
        mode: str
    ) -> Tuple[float, bool]:
        """
        套用 MOQ 約束（最高優先）
        
        - 乘數模式：Suggested_SS = max(SS_preliminary, MOQ × multiplier)
        - 加 1 模式：Suggested_SS = max(SS_preliminary, MOQ + 1)
        
        參數:
            preliminary_ss: 初步安全庫存
            moq: 最小訂購量
            multiplier: MOQ 乘數
            mode: MOQ 約束模式（"multiplier" 或 "add_one"）
            
        返回:
            (SS_after_MOQ, moq_constraint_applied)
            SS_after_MOQ 為整數（向上取整）
        """
        if mode == MOQ_MODE_MULTIPLIER:
            min_ss = moq * multiplier
        elif mode == MOQ_MODE_ADD_ONE:
            min_ss = moq + 1
        else:
            raise ValueError(f"無效的 MOQ 約束模式：{mode}")
        
        ss_after_moq = max(preliminary_ss, min_ss)
        moq_constraint_applied = ss_after_moq > preliminary_ss
        
        return math.ceil(ss_after_moq), moq_constraint_applied
    
    def apply_max_days_constraint(
        self,
        ss_after_moq: float,
        avg_daily_sales: float,
        max_days: int
    ) -> Tuple[int, bool]:
        """
        套用使用者設定的天數上限
        
        公式：Max_Allowed_SS = Avg_Daily_Sales × User_Max_Days
        Suggested_Safety_Stock = max(SS_after_MOQ, Max_Allowed_SS)
        
        參數:
            ss_after_moq: 套用 MOQ 約束後的安全庫存
            avg_daily_sales: 平均日銷量
            max_days: 天數上限
            
        返回:
            (Suggested_Safety_Stock, max_days_constraint_applied)
            Suggested_Safety_Stock 為整數（向上取整）
        """
        if avg_daily_sales <= 0:
            # 如果平均日銷量為 0 或負數，直接返回原值（向上取整）
            return math.ceil(ss_after_moq), False
        
        max_allowed_ss = avg_daily_sales * max_days
        suggested_ss = max(ss_after_moq, max_allowed_ss)
        max_days_constraint_applied = suggested_ss > ss_after_moq
        
        # 向上取整為整數
        return math.ceil(suggested_ss), max_days_constraint_applied
    
    def calculate_safety_stock_days(
        self,
        suggested_ss: float,
        avg_daily_sales: float
    ) -> float:
        """
        計算最終安全庫存可支撐的天數
        
        公式：Safety_Stock_Days = Suggested_Safety_Stock / Avg_Daily_Sales
        
        參數:
            suggested_ss: 建議安全庫存
            avg_daily_sales: 平均日銷量
            
        返回:
            支撐天數（保留 2 位小數）
        """
        if avg_daily_sales <= 0:
            return 0.0
        
        safety_stock_days = suggested_ss / avg_daily_sales
        return round(safety_stock_days, 2)
    
    def calculate_safety_stock(
        self,
        article: str,
        site: str,
        shop_class: str,
        last_month_qty: float,
        last_2_month_qty: float,
        supply_source: str,
        moq: float,
        original_safety_stock: Optional[float] = None,
        mtd_sold_qty: Optional[float] = None,
        product_hierarchy: Optional[str] = None,
        article_description: Optional[str] = None,
        rp_type: Optional[str] = None,
        target_qty: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        執行完整的安全庫存計算流程
        
        參數:
            article: 商品編號
            site: 門市代碼
            shop_class: 店舖等級
            last_month_qty: 上個月銷量
            last_2_month_qty: 前兩個月銷量總和
            supply_source: 供應來源
            moq: 最小訂購量
            original_safety_stock: 原始安全庫存（可選）
            mtd_sold_qty: 本月至今銷量（可選）
            target_qty: 目標數量（可選，如果存在則直接使用）
            
        返回:
            包含所有中間結果和最終結果的字典
        """
        # 步驟 1：計算平均日銷量
        avg_daily_sales = self.calculate_avg_daily_sales(
            last_month_qty,
            last_2_month_qty
        )
        
        # 檢查是否使用 Target Qty 模式
        use_target_qty = target_qty is not None and self.settings.use_target_qty_mode
        
        if use_target_qty:
            # Target Qty 模式：直接使用 Target Qty 作為 Safety Stock
            suggested_ss = math.ceil(target_qty)
            safety_stock_days = self.calculate_safety_stock_days(
                suggested_ss,
                avg_daily_sales
            )
            constraint_applied = "Target Qty"
            calculation_mode = "Target Qty"
            
            # Target Qty 模式的 Notes
            notes_parts = []
            notes_parts.append(f"計算步驟（Target Qty 模式）：")
            notes_parts.append(f"1. 平均日銷量 = ({last_month_qty} + {last_2_month_qty}) / 60 = {avg_daily_sales}")
            notes_parts.append(f"2. Target Qty = {target_qty}")
            notes_parts.append(f"3. Safety Stock = Target Qty = {suggested_ss}")
            notes_parts.append(f"4. 支撐天數 = {suggested_ss} / {avg_daily_sales} = {safety_stock_days} 天")
            notes_parts.append(f"計算模式：{calculation_mode}")
            notes = "\n".join(notes_parts)
            
            # 返回 Target Qty 模式結果
            return {
                "Article": article,
                "Site": site,
                "Class": shop_class,
                FIELD_RP_TYPE: rp_type if rp_type is not None else "",
                FIELD_ORIGINAL_SAFETY_STOCK: original_safety_stock if original_safety_stock is not None else 0,
                FIELD_MTD_SOLD_QTY: mtd_sold_qty if mtd_sold_qty is not None else 0,
                "Last_Month_Sold_Qty": last_month_qty,
                "Last_2_Month_Sold_Qty": last_2_month_qty,
                FIELD_PRODUCT_HIERARCHY: product_hierarchy if product_hierarchy is not None else "",
                FIELD_ARTICLE_DESCRIPTION: article_description if article_description is not None else "",
                FIELD_AVG_DAILY_SALES: avg_daily_sales,
                FIELD_LEAD_TIME_DAYS: 0,  # Target Qty 模式不使用前置時間
                FIELD_MF_USED: 0,  # Target Qty 模式不使用合併因素
                FIELD_MF_SERVICE_LEVEL: 0,  # Target Qty 模式不使用服務水準
                FIELD_PRELIMINARY_SS: 0,  # Target Qty 模式不計算初步安全庫存
                FIELD_SS_AFTER_MOQ: 0,  # Target Qty 模式不套用 MOQ 約束
                FIELD_USER_MAX_DAYS_APPLIED: 0,  # Target Qty 模式不套用天數上限
                FIELD_SUGGESTED_SAFETY_STOCK: suggested_ss,
                FIELD_CONSTRAINT_APPLIED: constraint_applied,
                FIELD_SAFETY_STOCK_DAYS: safety_stock_days,
                # Target Qty 模式的 Safety_Stock_Days
                "Preliminary_SS_Days": 0,
                "SS_after_MOQ_Days": 0,
                "Suggested_SS_Days": safety_stock_days,
                # Original_Safety_Stock_Days
                FIELD_ORIGINAL_SAFETY_STOCK_DAYS: round(original_safety_stock / avg_daily_sales, 2) if original_safety_stock is not None and avg_daily_sales > 0 else 0,
                # Target Safety Stock 欄位（預留給 Target Safety Stock 使用）
                FIELD_TARGET_SAFETY_STOCK: 0,
                FIELD_TARGET_SAFETY_STOCK_DAYS: 0,
                # 新增欄位
                "RP Type": rp_type if rp_type is not None else "",
                "Target_Qty_Used": True,
                "Calculation_Mode": calculation_mode,
                "Notes": notes
            }
        
        # 標準模式：使用原有的計算公式
        # 步驟 2：判斷前置時間
        lead_time = self.determine_lead_time(supply_source)
        
        # 步驟 3：取得合併因素
        mf_info = self.get_merge_factor(shop_class)
        mf = mf_info["value"]
        mf_service_level = mf_info["service_level"]
        
        # 步驟 4：計算初步安全庫存
        preliminary_ss = self.calculate_preliminary_ss(
            avg_daily_sales,
            lead_time,
            mf
        )
        
        # 步驟 5：套用 MOQ 約束
        ss_after_moq, moq_constraint_applied = self.apply_moq_constraint(
            preliminary_ss,
            moq,
            self.settings.moq_multiplier,
            self.settings.moq_constraint_mode
        )
        
        # 步驟 6：套用天數上限
        user_max_days = self.settings.get_max_days_for_shop_class(shop_class)
        suggested_ss, max_days_constraint_applied = self.apply_max_days_constraint(
            ss_after_moq,
            avg_daily_sales,
            user_max_days
        )
        
        # 步驟 7：計算支撐天數
        safety_stock_days = self.calculate_safety_stock_days(
            suggested_ss,
            avg_daily_sales
        )
        
        # 步驟 8：判斷約束條件
        if moq_constraint_applied and max_days_constraint_applied:
            constraint_applied = CONSTRAINT_BOTH
        elif moq_constraint_applied:
            constraint_applied = CONSTRAINT_MOQ
        elif max_days_constraint_applied:
            constraint_applied = CONSTRAINT_MAX_DAYS
        else:
            constraint_applied = CONSTRAINT_NONE

        calculation_mode = "Standard"

        # 步驟 9：生成 Notes 說明
        notes_parts = []
        notes_parts.append(f"計算步驟：")
        notes_parts.append(f"1. 平均日銷量 = ({last_month_qty} + {last_2_month_qty}) / 60 = {avg_daily_sales}")
        notes_parts.append(f"2. 前置時間 = {lead_time} 天 (Supply Source: {supply_source})")
        notes_parts.append(f"3. 合併因素 MF = {mf} (Shop Class: {shop_class}, 服務水準: {mf_service_level}%)")
        notes_parts.append(f"4. 初步安全庫存 = {avg_daily_sales} × √{lead_time} × {mf} = {preliminary_ss}")
        notes_parts.append(f"5. 套用 MOQ 約束：{moq} × {self.settings.moq_multiplier} = {moq * self.settings.moq_multiplier}")
        notes_parts.append(f"   → MOQ後安全庫存 = max({preliminary_ss}, {moq * self.settings.moq_multiplier}) = {ss_after_moq}")
        notes_parts.append(f"6. 套用天數上限：{avg_daily_sales} × {user_max_days} = {avg_daily_sales * user_max_days}")
        notes_parts.append(f"   → 建議安全庫存 = max({ss_after_moq}, {avg_daily_sales * user_max_days}) = {suggested_ss}")
        notes_parts.append(f"7. 支撐天數 = {suggested_ss} / {avg_daily_sales} = {safety_stock_days} 天")
        notes_parts.append(f"約束條件：{constraint_applied}")
        notes_parts.append(f"計算模式：{calculation_mode}")
        notes = "\n".join(notes_parts)

        # 返回所有結果
        return {
            "Article": article,
            "Site": site,
            "Class": shop_class,
            FIELD_RP_TYPE: rp_type if rp_type is not None else "",
            FIELD_ORIGINAL_SAFETY_STOCK: original_safety_stock if original_safety_stock is not None else 0,
            FIELD_MTD_SOLD_QTY: mtd_sold_qty if mtd_sold_qty is not None else 0,
            "Last_Month_Sold_Qty": last_month_qty,
            "Last_2_Month_Sold_Qty": last_2_month_qty,
            FIELD_PRODUCT_HIERARCHY: product_hierarchy if product_hierarchy is not None else "",
            FIELD_ARTICLE_DESCRIPTION: article_description if article_description is not None else "",
            FIELD_AVG_DAILY_SALES: avg_daily_sales,
            FIELD_LEAD_TIME_DAYS: lead_time,
            FIELD_MF_USED: mf,
            FIELD_MF_SERVICE_LEVEL: mf_service_level,
            FIELD_PRELIMINARY_SS: preliminary_ss,
            FIELD_SS_AFTER_MOQ: ss_after_moq,
            FIELD_USER_MAX_DAYS_APPLIED: user_max_days,
            FIELD_SUGGESTED_SAFETY_STOCK: suggested_ss,
            FIELD_CONSTRAINT_APPLIED: constraint_applied,
            FIELD_SAFETY_STOCK_DAYS: safety_stock_days,
            # 新增三個 Safety_Stock_Days 欄位
            "Preliminary_SS_Days": round(preliminary_ss / avg_daily_sales, 2) if avg_daily_sales > 0 else 0,
            "SS_after_MOQ_Days": round(ss_after_moq / avg_daily_sales, 2) if avg_daily_sales > 0 else 0,
            "Suggested_SS_Days": round(suggested_ss / avg_daily_sales, 2) if avg_daily_sales > 0 else 0,
            # 新增 Original_Safety_Stock_Days 欄位
            FIELD_ORIGINAL_SAFETY_STOCK_DAYS: round(original_safety_stock / avg_daily_sales, 2) if original_safety_stock is not None and avg_daily_sales > 0 else 0,
            # Target Safety Stock 欄位（預留給 Target Safety Stock 使用）
            FIELD_TARGET_SAFETY_STOCK: 0,
            FIELD_TARGET_SAFETY_STOCK_DAYS: 0,
            # 新增 RP Type 和 Notes 欄位
            "RP Type": rp_type if rp_type is not None else "",
            "Target_Qty_Used": False,
            "Calculation_Mode": calculation_mode,
            "Notes": notes
        }
