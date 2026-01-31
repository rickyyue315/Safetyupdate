"""
Core calculation module for Safety(Buffer) Stock Calculation
"""
import math
from typing import Dict, Any, Tuple, Optional
from datetime import date, datetime
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
    FIELD_TARGET_SAFETY_STOCK_DAYS,
    FIELD_SUGGESTED_DIFF,
    FIELD_TARGET_DIFF,
    FIELD_LAUNCH_DATE,
    FIELD_SELECTED_DATE,
    FIELD_MTD_DAYS,
    FIELD_LAST_MONTH_DAYS,
    FIELD_LAST_2_MONTH_DAYS,
    FIELD_MCH2,
    MCH2_MINIMUM_SS_MAP,
    CALCULATION_METHOD_DATE_BASED,
    FIELD_REGION,
    FIELD_SHOP_SIZE,
    SHOP_TYPE_SS_CONFIG
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
    
    def calculate_avg_daily_sales_with_date(
        self,
        mtd_qty: float,
        last_month_qty: float,
        last_2_month_qty: float,
        mtd_days: int,
        last_month_days: int,
        last_2_month_days: int,
        selected_date: Optional[date] = None,
        launch_date: Optional[date] = None
    ) -> Tuple[float, bool]:
        """
        基於日期計算平均日銷量（加權平均）
        
        公式：Avg_Daily_Sales = (MTD_Qty + Last_Month_Qty + Last_2_Month_Qty) /
                                    (MTD_Days + Last_Month_Days + Last_2_Month_Days)
        
        如果 Launch Date 存在且 Launch Date 到參考日期的天數少於總天數，
        則只計算 Launch Date 到參考日期的實際天數。
        
        參數:
            mtd_qty: 本月至今銷量
            last_month_qty: 上個月銷量
            last_2_month_qty: 前兩個月銷量總和
            mtd_days: 本月已過天數
            last_month_days: 上月總天數
            last_2_month_days: 前兩個月總天數
            selected_date: 選定的參考日期
            launch_date: 商品上市日期
            
        返回:
            (平均日銷量, 是否受 Launch Date 影響)
            平均日銷量（保留 2 位小數）
        """
        total_days = mtd_days + last_month_days + last_2_month_days
        
        if total_days <= 0:
            return 0.0, False
        
        total_qty = mtd_qty + last_month_qty + last_2_month_qty
        
        # 檢查 Launch Date 是否影響計算
        launch_date_affected = False
        actual_days = total_days
        
        if selected_date is not None and launch_date is not None:
            # Launch Date 已在呼叫處轉換為 date 類型
            # 計算 Launch Date 到參考日期的天數
            days_since_launch = (selected_date - launch_date).days + 1  # +1 包含 Launch Date 當天
            
            # 如果 Launch Date 到參考日期的天數少於總天數，使用實際天數
            if days_since_launch < total_days:
                actual_days = days_since_launch
                launch_date_affected = True
        
        if actual_days <= 0:
            return 0.0, launch_date_affected
        
        avg_daily_sales = total_qty / actual_days
        
        return round(avg_daily_sales, 2), launch_date_affected
    
    def get_shop_type_safety_stock(
        self,
        region: Optional[str],
        shop_class: str,
        shop_size: Optional[str]
    ) -> Optional[int]:
        """
        根據店舖類型查詢固定的安全庫存配置
        
        參數:
            region: 區域 (HK/MO)
            shop_class: 店舖等級 (AA/A1/A2/A3/B1/B2/C1/C2/D1)
            shop_size: 貨場面積 (XL/L/M/S/XS)
            
        返回:
            安全庫存數量（如果配置表中沒有則返回 None）
        """
        # 如果任何必要欄位為空，返回 None
        if not region or not shop_class or not shop_size:
            return None
        
        # 標準化輸入
        region = region.strip().upper()
        shop_class = shop_class.strip().upper()
        shop_size = shop_size.strip().upper()
        
        # 從 shop_class 中提取類別字母 (AA/A1/A2/A3 → A, B1/B2 → B, 等等)
        if shop_class in ["AA", "A1", "A2", "A3"]:
            class_category = "A"
        elif shop_class in ["B1", "B2"]:
            class_category = "B"
        elif shop_class in ["C1", "C2"]:
            class_category = "C"
        elif shop_class in ["D1"]:
            class_category = "D"
        else:
            return None
        
        # 查表
        try:
            return SHOP_TYPE_SS_CONFIG[region][class_category][shop_size]
        except KeyError:
            return None
    
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
    
    def apply_mch2_minimum_requirement(
        self,
        suggested_ss: float,
        mch2: Optional[str],
        shop_class: str
    ) -> Tuple[float, bool, int]:
        """
        套用 MCH2 最低安全庫存要求
        
        當 MCH2 為 "0302" 時，根據 Shop Class 應用最低安全庫存要求
        
        參數:
            suggested_ss: 建議安全庫存
            mch2: MCH2 欄位值（可以是字串或數字）
            shop_class: 店舖等級
            
        返回:
            (adjusted_ss, mch2_constraint_applied, mch2_minimum_required)
            adjusted_ss: 調整後的安全庫存
            mch2_constraint_applied: 是否應用了 MCH2 約束
            mch2_minimum_required: MCH2 最低要求值（若不適用則為 0）
        """
        # 將 MCH2 轉為字串並去除空白
        mch2_str = str(mch2).strip() if mch2 is not None else ""
        shop_class_upper = shop_class.upper() if shop_class else ""
        
        # 處理 MCH2 值：將 302 轉換為 0302，將 "0302" 保持為 "0302"
        if mch2_str == "302":
            mch2_str = "0302"
        elif mch2_str.isdigit() and len(mch2_str) == 3:
            # 如果是 3 位數字，自動補零成 4 位
            mch2_str = mch2_str.zfill(4)
        
        # 檢查 MCH2 是否為 "0302"
        if mch2_str != "0302":
            return suggested_ss, False, 0
        
        # 檢查該 MCH2 值是否有定義最低要求
        if mch2_str not in MCH2_MINIMUM_SS_MAP:
            return suggested_ss, False, 0
        
        # 檢查 Shop Class 是否有定義最低要求
        mch2_requirements = MCH2_MINIMUM_SS_MAP[mch2_str]
        if shop_class_upper not in mch2_requirements:
            return suggested_ss, False, 0
        
        # 取得最低要求值
        minimum_required = mch2_requirements[shop_class_upper]
        
        # 比較建議值與最低要求，取較大值
        adjusted_ss = max(suggested_ss, minimum_required)
        mch2_constraint_applied = adjusted_ss > suggested_ss
        
        return adjusted_ss, mch2_constraint_applied, minimum_required
    
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
        target_qty: Optional[float] = None,
        selected_date: Optional[str] = None,
        mtd_days: Optional[int] = None,
        last_month_days: Optional[int] = None,
        last_2_month_days: Optional[int] = None,
        launch_date: Optional[date] = None,
        mch2: Optional[str] = None,
        region: Optional[str] = None,
        shop_size: Optional[str] = None
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
            selected_date: 選定的參考日期（可選）
            mtd_days: MTD 天數（可選）
            last_month_days: 上月天數（可選）
            last_2_month_days: 前兩月天數（可選）
            launch_date: 商品上市日期（可選）
            mch2: MCH2 欄位值（可選）
            region: 區域 HK/MO（可選，用於店舖類型模式）
            shop_size: 貨場面積 XL/L/M/S/XS（可選，用於店舖類型模式）
            
        返回:
            包含所有中間結果和最終結果的字典
        """
        # 步驟 0-A：檢查是否使用店舖類型模式
        if self.settings.use_shop_type_mode:
            # 查詢店舖類型配置表
            shop_type_ss = self.get_shop_type_safety_stock(region, shop_class, shop_size)
            
            if shop_type_ss is not None:
                # 店舖類型模式：使用配置表中的固定值
                avg_daily_sales = self.calculate_avg_daily_sales(last_month_qty, last_2_month_qty)
                safety_stock_days = self.calculate_safety_stock_days(shop_type_ss, avg_daily_sales)
                
                notes = f"計算步驟（店舖類型模式）：\n"
                notes += f"區域: {region}, 店舖等級: {shop_class}, 貨場面積: {shop_size}\n"
                notes += f"查表得到固定安全庫存 = {shop_type_ss}"
                
                return {
                    "Article": article,
                    "Site": site,
                    "Class": shop_class,
                    FIELD_REGION: region if region else "",
                    FIELD_SHOP_SIZE: shop_size if shop_size else "",
                    FIELD_RP_TYPE: rp_type if rp_type is not None else "",
                    FIELD_ORIGINAL_SAFETY_STOCK: original_safety_stock if original_safety_stock is not None else 0,
                    FIELD_MTD_SOLD_QTY: mtd_sold_qty if mtd_sold_qty is not None else 0,
                    "Last_Month_Sold_Qty": last_month_qty,
                    "Last_2_Month_Sold_Qty": last_2_month_qty,
                    FIELD_PRODUCT_HIERARCHY: product_hierarchy if product_hierarchy is not None else "",
                    FIELD_ARTICLE_DESCRIPTION: article_description if article_description is not None else "",
                    FIELD_AVG_DAILY_SALES: avg_daily_sales,
                    FIELD_LEAD_TIME_DAYS: 0,
                    FIELD_MF_USED: 0,
                    FIELD_MF_SERVICE_LEVEL: 0,
                    FIELD_PRELIMINARY_SS: shop_type_ss,
                    FIELD_SS_AFTER_MOQ: shop_type_ss,
                    FIELD_USER_MAX_DAYS_APPLIED: 0,
                    FIELD_SUGGESTED_SAFETY_STOCK: shop_type_ss,
                    FIELD_CONSTRAINT_APPLIED: "店舖類型配置",
                    FIELD_SAFETY_STOCK_DAYS: safety_stock_days,
                    "Preliminary_SS_Days": safety_stock_days,
                    "SS_after_MOQ_Days": safety_stock_days,
                    "Suggested_SS_Days": safety_stock_days,
                    FIELD_ORIGINAL_SAFETY_STOCK_DAYS: round(original_safety_stock / avg_daily_sales, 2) if original_safety_stock and avg_daily_sales > 0 else 0,
                    FIELD_TARGET_SAFETY_STOCK: 0,
                    FIELD_TARGET_SAFETY_STOCK_DAYS: 0,
                    FIELD_SUGGESTED_DIFF: shop_type_ss - (original_safety_stock if original_safety_stock is not None else 0),
                    FIELD_TARGET_DIFF: 0,
                    "RP Type": rp_type if rp_type is not None else "",
                    "Target_Qty_Used": False,
                    "Calculation_Mode": "Shop Type Configuration",
                    "Notes": notes
                }
        
        # 步驟 0-B：檢查 RP Type 過濾條件
        # 如果設定為「僅計算 RF」且 RP Type 為 ND，則跳過計算
        if not self.settings.calculate_ss_for_all_rp_types:
            rp_type_upper = (rp_type.strip().upper() if rp_type else "").strip()
            if rp_type_upper == "ND":
                # RP Type 為 ND，且設定為「僅計算 RF」，則使用原始 Safety Stock
                safety_stock_days = round(original_safety_stock / (self.calculate_avg_daily_sales(last_month_qty, last_2_month_qty) if self.calculate_avg_daily_sales(last_month_qty, last_2_month_qty) > 0 else 1), 2) if original_safety_stock is not None else 0
                avg_daily_sales = self.calculate_avg_daily_sales(last_month_qty, last_2_month_qty)
                
                notes = f"計算步驟（跳過計算）：\n由於 RP Type = ND，且系統設定為「僅計算 RF」，本行使用原始 Safety Stock = {original_safety_stock if original_safety_stock is not None else 0}"
                
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
                    FIELD_LEAD_TIME_DAYS: 0,
                    FIELD_MF_USED: 0,
                    FIELD_MF_SERVICE_LEVEL: 0,
                    FIELD_PRELIMINARY_SS: 0,
                    FIELD_SS_AFTER_MOQ: 0,
                    FIELD_USER_MAX_DAYS_APPLIED: 0,
                    FIELD_SUGGESTED_SAFETY_STOCK: original_safety_stock if original_safety_stock is not None else 0,
                    FIELD_CONSTRAINT_APPLIED: "RP Type Filter (ND)",
                    FIELD_SAFETY_STOCK_DAYS: safety_stock_days,
                    "Preliminary_SS_Days": 0,
                    "SS_after_MOQ_Days": 0,
                    "Suggested_SS_Days": safety_stock_days,
                    FIELD_ORIGINAL_SAFETY_STOCK_DAYS: safety_stock_days,
                    FIELD_TARGET_SAFETY_STOCK: 0,
                    FIELD_TARGET_SAFETY_STOCK_DAYS: 0,
                    FIELD_SUGGESTED_DIFF: 0,
                    FIELD_TARGET_DIFF: 0,
                    "RP Type": rp_type if rp_type is not None else "",
                    "Target_Qty_Used": False,
                    "Calculation_Mode": "Skipped (RP Type=ND)",
                    "Notes": notes
                }
        
        # 步驟 1：計算平均日銷量
        # 檢查是否使用日期感知計算
        use_date_based_calculation = (
            selected_date is not None and
            mtd_days is not None and
            last_month_days is not None and
            last_2_month_days is not None and
            mtd_sold_qty is not None
        )

        # 準備參考日期對象
        selected_date_obj = None
        if selected_date is not None:
            selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # 處理 Launch Date（確保是 date 類型）
        launch_date_converted = None
        if launch_date is not None:
            # 如果是 Timestamp，轉換為 date
            if isinstance(launch_date, date) and not isinstance(launch_date, datetime):
                launch_date_converted = launch_date
            elif isinstance(launch_date, datetime):
                launch_date_converted = launch_date.date()
            else:
                # 嘗試使用 .date() 方法（針對 pandas Timestamp）
                try:
                    launch_date_converted = launch_date.date()
                except (AttributeError, TypeError):
                    launch_date_converted = launch_date

        # 初始化 Launch Date 影響標記
        launch_date_affected = False

        if use_date_based_calculation:
            # 使用日期感知計算（加權平均）
            avg_daily_sales, launch_date_affected = self.calculate_avg_daily_sales_with_date(
                mtd_sold_qty,
                last_month_qty,
                last_2_month_qty,
                mtd_days,
                last_month_days,
                last_2_month_days,
                selected_date_obj,
                launch_date_converted
            )
            calculation_method = CALCULATION_METHOD_DATE_BASED
        else:
            # 使用標準計算（固定60天）
            avg_daily_sales = self.calculate_avg_daily_sales(
                last_month_qty,
                last_2_month_qty
            )
            calculation_method = "Standard (60 Days)"
        
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
            
            # 計算 Suggested_Diff
            suggested_diff = suggested_ss - (original_safety_stock if original_safety_stock is not None else 0)
            
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
                # 差額欄位
                FIELD_SUGGESTED_DIFF: suggested_diff,
                FIELD_TARGET_DIFF: 0,
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
        
        # 步驟 6.5：套用 MCH2 最低安全庫存要求
        suggested_ss, mch2_constraint_applied, mch2_minimum_required = self.apply_mch2_minimum_requirement(
            suggested_ss,
            mch2,
            shop_class
        )
        
        # 步驟 7：計算支撐天數
        safety_stock_days = self.calculate_safety_stock_days(
            suggested_ss,
            avg_daily_sales
        )
        
        # 步驟 8：判斷約束條件
        if moq_constraint_applied and max_days_constraint_applied and mch2_constraint_applied:
            constraint_applied = "MOQ + 天數上限 + MCH2"
        elif moq_constraint_applied and max_days_constraint_applied:
            constraint_applied = CONSTRAINT_BOTH
        elif moq_constraint_applied and mch2_constraint_applied:
            constraint_applied = "MOQ + MCH2"
        elif max_days_constraint_applied and mch2_constraint_applied:
            constraint_applied = "天數上限 + MCH2"
        elif mch2_constraint_applied:
            constraint_applied = "MCH2"
        elif moq_constraint_applied:
            constraint_applied = CONSTRAINT_MOQ
        elif max_days_constraint_applied:
            constraint_applied = CONSTRAINT_MAX_DAYS
        else:
            constraint_applied = CONSTRAINT_NONE

        calculation_mode = calculation_method

        # 步驟 9：生成 Notes 說明
        notes_parts = []
        notes_parts.append(f"計算步驟：")

        if use_date_based_calculation:
            notes_parts.append(f"0. 日期感知計算模式")
            notes_parts.append(f"   - 選定參考日期：{selected_date}")
            notes_parts.append(f"   - 當月(1月)天數：{mtd_days}天")
            notes_parts.append(f"   - 上月(12月)天數：{last_month_days}天")
            notes_parts.append(f"   - 前兩月(11月)天數：{last_2_month_days}天")
            if launch_date is not None:
                notes_parts.append(f"   - Launch Date：{launch_date}")
            notes_parts.append(f"1. 平均日銷量（加權平均，基於實際天數）")
            notes_parts.append(f"   - MTD 銷量 = {mtd_sold_qty}")
            notes_parts.append(f"   - 上月銷量 = {last_month_qty}")
            notes_parts.append(f"   - 前兩月銷量 = {last_2_month_qty}")
            notes_parts.append(f"   - 平均日銷量 = ({mtd_sold_qty} + {last_month_qty} + {last_2_month_qty}) / ({mtd_days} + {last_month_days} + {last_2_month_days}) = {avg_daily_sales}")
            # 如果受 Launch Date 影響，添加提示
            if launch_date_affected:
                notes_parts.append(f"   - Launch Date 影響計算，只計算Launch Date到參考日期的實際天數")
        else:
            notes_parts.append(f"1. 平均日銷量 = ({last_month_qty} + {last_2_month_qty}) / 60 = {avg_daily_sales}")
        notes_parts.append(f"2. 前置時間 = {lead_time} 天 (Supply Source: {supply_source})")
        notes_parts.append(f"3. 合併因素 MF = {mf} (Shop Class: {shop_class}, 服務水準: {mf_service_level}%)")
        notes_parts.append(f"4. 初步安全庫存 = {avg_daily_sales} × √{lead_time} × {mf} = {preliminary_ss}")
        notes_parts.append(f"5. 套用 MOQ 約束：{moq} × {self.settings.moq_multiplier} = {moq * self.settings.moq_multiplier}")
        notes_parts.append(f"   → MOQ後安全庫存 = max({preliminary_ss}, {moq * self.settings.moq_multiplier}) = {ss_after_moq}")
        notes_parts.append(f"6. 套用天數上限：{avg_daily_sales} × {user_max_days} = {avg_daily_sales * user_max_days}")
        notes_parts.append(f"   → 建議安全庫存 = max({ss_after_moq}, {avg_daily_sales * user_max_days}) = {suggested_ss}")
        if mch2_constraint_applied:
            notes_parts.append(f"7. 套用 MCH2 最低要求：MCH2 = {mch2}, Class = {shop_class}, 最低要求 = {mch2_minimum_required}")
            notes_parts.append(f"   → 最終安全庫存 = max({suggested_ss}, {mch2_minimum_required}) = {suggested_ss}")
        else:
            notes_parts.append(f"7. 支撐天數 = {suggested_ss} / {avg_daily_sales} = {safety_stock_days} 天")
        notes_parts.append(f"約束條件：{constraint_applied}")
        notes_parts.append(f"計算模式：{calculation_mode}")
        notes = "\n".join(notes_parts)

        # 計算 Suggested_Diff
        suggested_diff = suggested_ss - (original_safety_stock if original_safety_stock is not None else 0)

        # 返回所有結果
        result = {
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
            # 差額欄位
            FIELD_SUGGESTED_DIFF: suggested_diff,
            FIELD_TARGET_DIFF: 0,
            # 新增 RP Type 和 Notes 欄位
            "RP Type": rp_type if rp_type is not None else "",
            "Target_Qty_Used": False,
            "Calculation_Mode": calculation_mode,
            # 新增 MCH2 相關欄位
            "MCH2": mch2 if mch2 is not None else "",
            "MCH2_Minimum_Required": mch2_minimum_required if mch2_constraint_applied else 0,
            "MCH2_Minimum_SS_Applied": mch2_constraint_applied,
            "Notes": notes
        }
        
        # 添加日期相關欄位（如果使用日期感知計算）
        if use_date_based_calculation:
            result[FIELD_SELECTED_DATE] = selected_date
            result[FIELD_MTD_DAYS] = mtd_days
            result[FIELD_LAST_MONTH_DAYS] = last_month_days
            result[FIELD_LAST_2_MONTH_DAYS] = last_2_month_days
        
        return result
