"""
Safety(Buffer) Stock Calculation - Main Application
安全(緩衝)庫存計算機 - 主應用程式
"""
import streamlit as st
import io
from pathlib import Path


# 設定頁面配置
st.set_page_config(
    page_title="安全(緩衝)庫存計算機",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=3600, show_spinner="載入設定中...")
def load_settings() -> 'Settings':
    """
    載入或建立預設設定（使用快取）
    
    返回:
        Settings 實例
    """
    from config.settings import Settings
    
    settings_file = "config/settings.json"
    return Settings.load_from_file(settings_file)


def save_settings(settings: 'Settings'):
    """
    儲存設定到檔案
    
    參數:
        settings: 要儲存的設定
    """
    from config.settings import Settings
    
    settings_file = "config/settings.json"
    settings.save_to_file(settings_file)


def display_home_page():
    """顯示首頁"""
    st.title("📦 安全(緩衝)庫存計算機 v2.0")
    st.markdown("---")
    
    st.markdown("""
    ## 系統簡介
    
    本系統根據實際可用資料欄位及商業限制，計算合理的安全庫存建議值。
    """)
    
    # SAP 資料匯出說明
    with st.expander("📋 SAP 資料匯出說明", expanded=False):
        st.markdown("""
        ### 從 SAP 系統匯出資料步驟
        
        1. **SAP 程式碼**：`ZRPMM0015_S`
        
        2. **Get Variant**：`ACTIVE SHOP`
        
        3. **更改 Output Layout**：`/SHOP 3M`
        
        4. **輸入 SKU**：輸入要查詢的商品編號
        
        5. **轉出成 Excel report**：執行程式並匯出為 Excel 格式
        
        6. **在 Excel 內新增 Class (店舖級別)**：手動新增店舖等級欄位
        
        ---
        
        ### 店舖級別說明
        
        店舖級別（Class）可能的值包括：
        - AA, A1, A2, A3
        - B1, B2
        - C1, C2
        - D1
        
        > 💡 **提示**：確保 Excel 檔案包含所有必要欄位後再上傳至本系統進行計算。
        """)
    
    st.markdown("""
    ### 核心功能
    
    - **智能計算**: 根據平均日銷量、前置時間和合併因素計算安全庫存
    - **MOQ 約束**: 自動套用最小訂購量約束（支援乘數模式和加 1 模式）
    - **天數上限**: 支援自訂安全庫存天數上限（7-14 天）
    - **Target Qty 模式**: 支援直接使用輸入資料中的 `Target Qty` 作為安全庫存
    - **Target Safety Stock 模式**: 支援輸入 SKU 總目標數量，系統自動按比例分配至各店舖
    - **多種輸入**: 支援 CSV 和 Excel 檔案輸入
    - **結果匯出**: 可匯出計算結果為 Excel 或 CSV 格式，包含詳細的 SKU 統計摘要
    
    ### 計算公式
    
    #### 1. 標準模式 (Standard Mode)
    1. **初步安全庫存**: SS_preliminary = Avg_Daily_Sales × √Lead_Time_Days × MF
    2. **套用 MOQ 約束**: SS_after_MOQ = max(SS_preliminary, MOQ × multiplier)
    3. **套用天數上限**: Suggested_Safety_Stock = min(SS_after_MOQ, Avg_Daily_Sales × Max_Days)
    
    #### 2. Target Qty 模式
    - 直接使用輸入資料中的 `Target Qty` 作為安全庫存值。
    
    #### 3. Target Safety Stock 模式
    - 根據輸入的 SKU 總目標數量，按標準模式計算出的比例分配至各店舖。
    
    ### Class 權重說明
    
    系統支援 Target Safety Stock 模式，可按店舖等級 (Class) 權重比例分配 SKU 目標數量至各店舖：
    
    - **Class A (AA, A1, A2, A3)**：權重 A（預設 3）
    - **Class B (B1, B2)**：權重 B（預設 2）
    - **Class C (C1, C2)**：權重 C（預設 1）
    - **Class D (D1)**：權重 D（預設 1）
    
    **分配邏輯**：
    1. 計算總權重：`Total_Weight = Σ Weight_i`
    2. 計算分配係數：`Factor = SKU_Total_Target / Total_Weight`
    3. 初步分配：`Allocated_i = floor(Weight_i × Factor)`
    4. 計算餘數：`Remainder = SKU_Total_Target - Σ Allocated_i`
    5. 將餘數分配給小數部分最大的店舖（每個店舖加 1）
    6. 確保總和等於目標數量
    
    **預設分配比例**：A : B : C : D = 3 : 2 : 1 : 1
    
    可在系統設定中自訂各類別的權重（範圍：1-100），權重越大，分配的數量越多。
    
    ### 使用說明
    
    1. 在「計算」頁面上傳您的資料檔案
    2. 在側邊欄調整系統設定（可選）
    3. 如果需要按 SKU 總量分配，在計算頁面的「SKU 目標數量分配」表格中輸入數值
    4. 點擊「開始計算」按鈕
    5. 查看計算結果並匯出（如需要）
    
    ### 輸入資料格式
    
    您的資料檔案必須包含以下欄位：
    
    - **Article**: 商品編號
    - **Site**: 門市代碼
    - **Class**: 店舖等級（AA, A1, A2, A3, B1, B2, C1, C2, D1）
    - **Last Month Sold Qty**: 上個月銷量
    - **Last 2 Month Sold Qty**: 前兩個月銷量總和
    - **Supply Source**: 供應來源代碼（1, 2, 4 等）
    - **MOQ**: 最小訂購量
    - **Target Qty** (可選): 目標數量
    """)


def display_settings_panel(settings: 'Settings') -> 'Settings':
    """
    顯示設定面板並返回更新後的設定
    
    參數:
        settings: 當前設定
        
    返回:
        更新後的設定
    """
    from config.settings import Settings
    
    st.sidebar.title("⚙️ 系統設定")
    
    st.sidebar.markdown("---")
    
    # 全域天數上限設定
    st.sidebar.subheader("全域天數上限")
    max_days = st.sidebar.slider(
        "安全庫存天數上限",
        min_value=3,
        max_value=21,
        value=settings.max_safety_stock_days,
        help="所有店舖的預設天數上限（3-21 天）"
    )
    
    # MOQ 約束設定
    st.sidebar.subheader("MOQ 約束設定")
    moq_mode = st.sidebar.selectbox(
        "MOQ 約束模式",
        ["multiplier", "add_one"],
        index=0 if settings.moq_constraint_mode == "multiplier" else 1,
        help="選擇 MOQ 約束的計算模式"
    )
    
    moq_multiplier = st.sidebar.number_input(
        "MOQ 約束乘數",
        min_value=0.1,
        max_value=10.0,
        value=settings.moq_multiplier,
        step=0.05,
        format="%.2f",
        help="乘數模式下的 MOQ 乘數（預設 1.25）"
    )
    
    # 按 Shop Class 設定天數上限
    st.sidebar.subheader("按 Shop Class 設定")
    enable_custom_max_days = st.sidebar.checkbox(
        "啟用自訂 Shop Class 天數上限",
        value=len(settings.shop_class_max_days) > 0,
        help="為不同的 Shop Class 設定不同的天數上限"
    )
    
    shop_class_max_days = {}
    if enable_custom_max_days:
        st.sidebar.markdown("**自訂天數上限**")
        valid_shop_classes = ["AA", "A1", "A2", "A3", "B1", "B2", "C1", "C2", "D1"]
        for shop_class in valid_shop_classes:
            custom_max = st.sidebar.number_input(
                f"{shop_class} 天數上限",
                min_value=3,
                max_value=21,
                value=settings.shop_class_max_days.get(shop_class, max_days),
                key=f"max_days_{shop_class}",
                help=f"Shop Class {shop_class} 的天數上限（留空使用全域設定）"
            )
            if custom_max != max_days:
                shop_class_max_days[shop_class] = custom_max
    
    # Target Qty 模式設定
    st.sidebar.markdown("---")
    st.sidebar.subheader("Target Qty 模式")
    use_target_qty_mode = st.sidebar.checkbox(
        "啟用 Target Qty 模式",
        value=settings.use_target_qty_mode,
        help="如果輸入檔案包含 'Target Qty' 欄位，直接使用 Target Qty 作為 Safety Stock（跳過原有計算公式）"
    )
    
    # 顯示 Target Qty 模式說明
    if use_target_qty_mode:
        st.sidebar.info(
            "📋 **Target Qty 模式說明**\n\n"
            "當啟用此模式時：\n"
            "• 如果資料包含 'Target Qty' 欄位，直接使用該值作為 Safety Stock\n"
            "• 跳過原有的 MF、MOQ 約束、天數上限計算\n"
            "• 適合用於按未來一個月的銷售預測來設定 Safety Stock"
        )
    
    # Class 權重設定
    st.sidebar.markdown("---")
    st.sidebar.subheader("Class 權重設定")
    st.sidebar.markdown("**用於 SKU 目標數量分配**")
    
    enable_custom_class_weights = st.sidebar.checkbox(
        "啟用自訂 Class 權重",
        value=settings.class_weights is not None and settings.class_weights != {"A": 3, "B": 2, "C": 1, "D": 1},
        help="為不同的 Class 類別設定自訂權重（預設：A=3, B=2, C=1, D=1）"
    )
    
    class_weights = {}
    if enable_custom_class_weights:
        st.sidebar.markdown("**自訂權重**")
        valid_class_categories = ["A", "B", "C", "D"]
        for category in valid_class_categories:
            custom_weight = st.sidebar.number_input(
                f"Class {category} 權重",
                min_value=1,
                max_value=100,
                value=settings.class_weights.get(category, {"A": 3, "B": 2, "C": 1, "D": 1}[category]),
                key=f"class_weight_{category}",
                help=f"Class {category} 的分配權重（預設：A=3, B=2, C=1, D=1）"
            )
            class_weights[category] = custom_weight
    else:
        # 使用預設權重
        class_weights = {"A": 3, "B": 2, "C": 1, "D": 1}
    
    # 顯示權重說明
    st.sidebar.info(
        "📋 **Class 權重說明**\n\n"
        "權重用於 SKU 目標數量分配：\n"
        "• Class A (AA, A1, A2, A3)：權重 A\n"
        "• Class B (B1, B2)：權重 B\n"
        "• Class C (C1, C2)：權重 C\n"
        "• Class D (D1)：權重 D\n"
        "• 權重越大，分配的數量越多"
    )
    
    # 建立新設定
    new_settings = Settings(
        max_safety_stock_days=max_days,
        moq_multiplier=moq_multiplier,
        moq_constraint_mode=moq_mode,
        shop_class_max_days=shop_class_max_days if enable_custom_max_days else {},
        use_target_qty_mode=use_target_qty_mode,
        class_weights=class_weights
    )
    
    # 按鈕區域
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # Reset 按鈕
        if st.sidebar.button("🔄 重置設定"):
            # 建立預設設定
            default_settings = Settings()
            # 儲存預設設定
            save_settings(default_settings)
            # 顯示成功訊息
            st.sidebar.success("設定已重置為預設值！")
            # 重新載入頁面以更新 UI
            st.rerun()
    with col2:
        # 儲存設定按鈕
        if st.sidebar.button("💾 儲存設定"):
            save_settings(new_settings)
            st.sidebar.success("設定已儲存！")
    
    return new_settings


def display_file_uploader():
    """
    顯示檔案上傳介面
    
    返回:
        上傳的 DataFrame，如果未上傳則返回 None
    """
    from core.data_processor import DataProcessor
    
    st.subheader("📤 上傳資料檔案")
    
    uploaded_file = st.file_uploader(
        "選擇 CSV 或 Excel 檔案",
        type=['csv', 'xlsx', 'xls'],
        help="支援 .csv、.xlsx、.xls 格式"
    )
    
    if uploaded_file is not None:
        try:
            # 儲存上傳的檔案
            file_path = Path(f"data/input/{uploaded_file.name}")
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # 載入資料
            df = DataProcessor.load_data(str(file_path))
            
            # 驗證必要欄位
            if DataProcessor.validate_required_columns(df):
                st.success(f"✅ 成功載入 {len(df)} 筆記錄")
                return df
            else:
                missing = DataProcessor.get_missing_columns(df)
                st.error(f"❌ 資料檔案缺少必要欄位：{', '.join(missing)}")
                return None
                
        except Exception as e:
            st.error(f"❌ 載入檔案時發生錯誤：{str(e)}")
            return None
    
    return None


def display_results_summary(results_df: 'pd.DataFrame'):
    """
    顯示計算結果摘要和表格
    
    參數:
        results_df: 包含計算結果的 DataFrame
    """
    import pandas as pd
    
    st.subheader("📊 計算結果")
    
    # 顯示統計摘要
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("總記錄數", len(results_df))
    with col2:
        moq_count = (results_df['Constraint_Applied'] == 'MOQ').sum()
        st.metric("觸發 MOQ 約束", moq_count)
    with col3:
        max_days_count = (results_df['Constraint_Applied'] == '天數上限').sum()
        st.metric("觸發天數上限", max_days_count)
    with col4:
        avg_days = results_df['Safety_Stock_Days'].mean()
        st.metric("平均支撐天數", f"{avg_days:.2f}")
    
    st.markdown("---")
    
    # 顯示結果表格
    st.markdown("### 詳細結果")
    
    # 定義欄位顯示順序
    display_columns = [
        'Article', 'Site', 'Class',
        'RP Type',                # 新增
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
    
    # 重新排列欄位
    results_df = results_df[display_columns]
    
    # 顯示可編輯的表格
    st.dataframe(
        results_df,
        use_container_width=True,
        height=400
    )
    
    # 高亮顯示約束記錄
    st.markdown("---")
    st.markdown("### 約束記錄分析")
    
    constraint_types = results_df['Constraint_Applied'].value_counts()
    if len(constraint_types) > 0:
        st.bar_chart(constraint_types)


def display_download_buttons(results_df: 'pd.DataFrame'):
    """
    顯示下載按鈕
    
    參數:
        results_df: 包含計算結果的 DataFrame
    """
    import pandas as pd
    
    st.markdown("---")
    st.subheader("💾 匯出結果")
    
    # Excel 匯出
    try:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # 結果工作表 - 調整欄位順序
            display_columns = [
                'Article', 'Site', 'Class',
                'RP Type',                # 新增
                'Product Hierarchy',      # 新增
                'Article Description',    # 新增
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
            existing_columns = [col for col in display_columns if col in results_df.columns]
            
            # 確保 Article 欄位以文字格式輸出
            results_df_copy = results_df.copy()
            if 'Article' in results_df_copy.columns:
                results_df_copy['Article'] = results_df_copy['Article'].astype(str)
            
            results_df_copy.to_excel(writer, sheet_name='Results', index=False, columns=existing_columns)
            
            # 統計摘要工作表 - 全體統計
            summary_data = {
                "項目": [
                    "總記錄數",
                    "觸發 MOQ 約束記錄數",
                    "觸發天數上限記錄數",
                    "平均支撐天數"
                ],
                "數值": [
                    len(results_df),
                    (results_df['Constraint_Applied'] == 'MOQ').sum(),
                    (results_df['Constraint_Applied'] == '天數上限').sum(),
                    results_df['Safety_Stock_Days'].mean()
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False, startrow=0)
            
            # 新增按 SKU 分類的統計
            if 'Article' in results_df.columns:
                sku_summary = results_df.groupby('Article').agg({
                    'Site': 'count',
                    'Product Hierarchy': 'first',
                    'Article Description': 'first',
                    'Original_Safety_Stock': 'sum',
                    'MTD_Sold_Qty': 'sum',
                    'Last_Month_Sold_Qty': 'sum',
                    'Last_2_Month_Sold_Qty': 'sum',
                    'Suggested_Safety_Stock': 'sum',
                    'Safety_Stock_Days': 'mean',
                    'Target_Safety_Stock': 'sum',
                    'Target_Safety_Stock_Days': 'mean'
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
                    '平均支撐天數',
                    'Target Safety Stock 總和',
                    'Target Safety Stock 平均天數'
                ]
                
                # 寫入 SKU 摘要到 Summary 工作表（從第 6 行開始）
                sku_summary.to_excel(writer, sheet_name='Summary', index=False, startrow=len(summary_df) + 2)
        
        excel_buffer.seek(0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📊 下載 Excel 檔案",
                data=excel_buffer,
                file_name=f"safety_stock_results_{pd.Timestamp.now(tz='Asia/Hong_Kong').strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # CSV 匯出
        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_buffer.seek(0)
        
        with col2:
            st.download_button(
                label="📄 下載 CSV 檔案",
                data=csv_buffer.getvalue(),
                file_name=f"safety_stock_results_{pd.Timestamp.now(tz='Asia/Hong_Kong').strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ 生成下載檔案時發生錯誤：{str(e)}")


# 將 Class 類別映射到權重類別
CLASS_CATEGORY_MAP = {
    "AA": "A", "A1": "A", "A2": "A", "A3": "A",
    "B1": "B", "B2": "B",
    "C1": "C", "C2": "C",
    "D1": "D"
}


def calculate_safety_stock(df: 'pd.DataFrame', settings: 'Settings', sku_targets: dict = None) -> 'pd.DataFrame':
    """
    對資料執行安全庫存計算
    
    參數:
        df: 輸入資料 DataFrame
        settings: 系統設定
        sku_targets: SKU 目標數量字典 {sku: target_qty}
        
    返回:
        包含計算結果的 DataFrame
    """
    import pandas as pd
    import math
    from core.calculator import SafetyStockCalculator
    from core.data_processor import DataProcessor
    
    # 建立計算器
    calculator = SafetyStockCalculator(settings)
    
    # 準備計算資料
    records = DataProcessor.prepare_calculation_data(df)
    
    # 執行計算
    results = []
    for record in records:
        try:
            result = calculator.calculate_safety_stock(
                article=record['Article'],
                site=record['Site'],
                shop_class=record['Class'],
                last_month_qty=record['Last Month Sold Qty'],
                last_2_month_qty=record['Last 2 Month Sold Qty'],
                supply_source=str(record['Supply Source']),
                moq=record['MOQ'],
                original_safety_stock=record.get('Original_Safety_Stock'),
                mtd_sold_qty=record.get('MTD_Sold_Qty'),
                product_hierarchy=record.get('Product Hierarchy'),
                article_description=record.get('Article Description'),
                rp_type=record.get('RP Type'),
                target_qty=record.get('Target Qty')
            )
            results.append(result)
        except Exception as e:
            st.error(f"計算記錄 {record['Article']} - {record['Site']} 時發生錯誤：{str(e)}")
    
    # 轉換為 DataFrame
    results_df = pd.DataFrame(results)
    
    # 如果有 SKU 目標數量，執行分配邏輯 (按 Class 權重分配)
    if sku_targets and len(results_df) > 0:
        # 確保 Article 欄位類型一致
        results_df['Article'] = results_df['Article'].astype(str)
        
        for sku, target_qty in sku_targets.items():
            if target_qty <= 0:
                continue
                
            sku = str(sku)
            # 篩選該 SKU 的所有記錄
            sku_mask = results_df['Article'] == sku
            sku_records = results_df[sku_mask]
            
            if len(sku_records) == 0:
                continue
            
            # 按 Class 權重分配邏輯
            # 1. 取得每個店舖的 Class 權重類別
            sku_records = sku_records.copy()
            sku_records['Weight_Category'] = sku_records['Class'].map(CLASS_CATEGORY_MAP).fillna("D")
            
            # 2. 使用設定中的權重
            sku_records['Weight'] = sku_records['Weight_Category'].map(settings.class_weights).fillna(1)
            
            # 3. 計算總權重
            total_weight = sku_records['Weight'].sum()
            
            if total_weight > 0:
                # 3. 計算分配係數 (每單位權重分配的數量)
                factor = target_qty / total_weight
                
                # 4. 初步分配 (向下取整)
                allocated_ss = (sku_records['Weight'] * factor).apply(math.floor)
                
                # 5. 計算餘數
                current_allocated_sum = allocated_ss.sum()
                remainder = int(target_qty - current_allocated_sum)
                
                # 6. 分配餘數 (分配給計算後數值小數部分最大的店舖)
                if remainder > 0:
                    # 計算小數部分
                    fractional_parts = (sku_records['Weight'] * factor) - allocated_ss
                    # 排序並取前 remainder 個店舖的 index
                    top_indices = fractional_parts.sort_values(ascending=False).head(remainder).index
                    # 加 1
                    allocated_ss.loc[top_indices] += 1
                
                # 7. 更新 DataFrame - 將分配結果寫入 Target_Safety_Stock，保留 Suggested_Safety_Stock
                results_df.loc[sku_mask, 'Target_Safety_Stock'] = allocated_ss.values
                results_df.loc[sku_mask, 'Constraint_Applied'] = 'Target Safety Stock'
                results_df.loc[sku_mask, 'Calculation_Mode'] = 'Target Safety Stock'
                
                # 8. 更新 Notes 和其他相關欄位
                for idx in sku_mask[sku_mask].index:
                    shop_class = results_df.loc[idx, 'Class']
                    weight = sku_records.loc[idx, 'Weight']
                    new_ss = results_df.loc[idx, 'Target_Safety_Stock']
                    avg_daily_sales = results_df.loc[idx, 'Avg_Daily_Sales']
                    original_ss = results_df.loc[idx, 'Original_Safety_Stock']
                    
                    # 計算 Target_Diff
                    target_diff = new_ss - original_ss
                    results_df.loc[idx, 'Target_Diff'] = target_diff
                    
                    # 更新 Target Safety Stock 的支撐天數
                    if avg_daily_sales > 0:
                        new_days = round(new_ss / avg_daily_sales, 2)
                    else:
                        new_days = 0
                    results_df.loc[idx, 'Target_Safety_Stock_Days'] = new_days
                    
                    # 更新 Notes
                    old_notes = results_df.loc[idx, 'Notes']
                    allocation_note = (
                        f"\n\n--- Target Safety Stock (按 Class 權重分配) ---\n"
                        f"Target Qty: {target_qty}\n"
                        f"Class: {shop_class}, Weight: {weight}\n"
                        f"Total Weight: {total_weight}\n"
                        f"Allocation Factor: {factor:.4f}\n"
                        f"Allocated SS: {new_ss}\n"
                        f"Target Diff: {target_diff}"
                    )
                    results_df.loc[idx, 'Notes'] = old_notes + allocation_note

    return results_df


def main():
    """主程式"""
    import pandas as pd
    
    # 初始化 session state
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'calculation_timestamp' not in st.session_state:
        st.session_state.calculation_timestamp = None
    
    # 載入設定
    settings = load_settings()
    
    # 建立頁面導航
    page = st.sidebar.radio(
        "選擇頁面",
        ["🏠 首頁", "🧮 計算"],
        label_visibility="collapsed"
    )
    
    # 顯示設定面板（在所有頁面）
    settings = display_settings_panel(settings)
    
    # 根據選擇的頁面顯示內容
    if page == "🏠 首頁":
        display_home_page()
    elif page == "🧮 計算":
        # 顯示檔案上傳
        df = display_file_uploader()
        
        # 如果有資料，顯示計算按鈕
        if df is not None:
            st.markdown("---")
            
            # 顯示資料預覽
            with st.expander("📋 查看原始資料"):
                st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            
            # SKU Target Qty Allocation Section
            st.subheader("🎯 SKU 目標數量分配 (Target Safety Stock)")
            st.info(f"在此輸入 SKU 的總目標數量，系統將自動按店舖等級 (Class) 比例分配至各店舖。\n\n**分配比例**：Class A (AA, A1, A2, A3) : Class B (B1, B2) : Class C (C1, C2) : Class D (D1) = {settings.class_weights.get('A', 3)} : {settings.class_weights.get('B', 2)} : {settings.class_weights.get('C', 1)} : {settings.class_weights.get('D', 1)}\n\n💡 提示：您可以在左側「系統設定」中自訂各類別的權重。\n\n若輸入 0 則使用標準計算公式。")
            
            # 檢查可選欄位是否存在
            has_product_hierarchy = 'Product Hierarchy' in df.columns
            has_article_description = 'Article Description' in df.columns
            
            # 準備 SKU 編輯表格
            unique_skus = sorted(df['Article'].unique().astype(str))
            sku_target_data = []
            
            for sku in unique_skus:
                # 直接找到該 SKU 在原始 df 中的第一行資料
                # 確保比較時類型一致（將 Article 欄位轉為字串）
                sku_rows = df[df['Article'].astype(str) == sku]
                
                if len(sku_rows) > 0:
                    sku_first_row = sku_rows.iloc[0]
                    
                    # 從第一行提取資料
                    product_hierarchy = sku_first_row['Product Hierarchy'] if has_product_hierarchy else ""
                    article_description = sku_first_row['Article Description'] if has_article_description else ""
                    
                    # 處理 NaN 值
                    if pd.isna(product_hierarchy):
                        product_hierarchy = ""
                    if pd.isna(article_description):
                        article_description = ""
                else:
                    # 如果沒有找到該 SKU 的資料，使用空值
                    product_hierarchy = ""
                    article_description = ""
                
                sku_target_data.append({
                    "SKU": sku,
                    "Product Hierarchy": product_hierarchy,
                    "Article Description": article_description,
                    "Target Qty": 0
                })
            
            sku_target_df = pd.DataFrame(sku_target_data)
            
            # 建立基礎 column_config
            column_config = {
                "SKU": st.column_config.TextColumn("SKU (Article)", disabled=True),
                "Target Qty": st.column_config.NumberColumn(
                    "Target Qty",
                    min_value=0,
                    step=1,
                    format="%d",
                    help="輸入該 SKU 的總目標數量"
                )
            }
            
            # 如果欄位存在，加入 column_config
            if has_product_hierarchy:
                column_config["Product Hierarchy"] = st.column_config.TextColumn(
                    "Product Hierarchy",
                    disabled=True,
                    help="產品階層"
                )
            
            if has_article_description:
                column_config["Article Description"] = st.column_config.TextColumn(
                    "Article Description",
                    disabled=True,
                    width="large",
                    help="商品描述"
                )
            
            # 顯示編輯器
            edited_sku_df = st.data_editor(
                sku_target_df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                key="sku_target_editor"
            )
            
            # 轉換為字典
            sku_targets = {}
            if edited_sku_df is not None:
                for _, row in edited_sku_df.iterrows():
                    if row['Target Qty'] > 0:
                        sku_targets[str(row['SKU'])] = row['Target Qty']
            
            st.markdown("---")

            # 計算按鈕
            if st.button("🚀 開始計算", type="primary", use_container_width=True):
                with st.spinner("正在計算中..."):
                    results_df = calculate_safety_stock(df, settings, sku_targets)
                    
                    if len(results_df) > 0:
                        # 保存到 session state
                        st.session_state.results_df = results_df
                        st.session_state.calculation_timestamp = pd.Timestamp.now(tz='Asia/Hong_Kong')
                        
                        st.success(f"✅ 計算完成！共處理 {len(results_df)} 筆記錄")
                        display_results_summary(results_df)
        
        # 如果有計算結果，顯示下載按鈕
        if st.session_state.results_df is not None:
            st.markdown("---")
            st.info(f"📅 計算時間：{st.session_state.calculation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            display_download_buttons(st.session_state.results_df)


if __name__ == "__main__":
    main()
