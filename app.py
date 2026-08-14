import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="衛保組衛材管理系統", layout="wide", page_icon="🏥")

# ==============================================================================
# 🎨 清新風格 & 字體加大 CSS 樣式設定
# ==============================================================================
st.markdown(
    """
    <style>
    /* 1. 全域字體與背景 */
    html, body, [class*="css"] {
        font-family: "PingFang TC", "Microsoft JhengHei", "Helvetica Neue", sans-serif;
    }
    
    /* 網頁主體背景：乾淨舒服的微藍綠灰色 */
    .stApp {
        background-color: #f5f8f6;
    }

    /* 2. 全域文字字體加大 */
    p, div, span, label, input, select {
        font-size: 1.15rem !important;
        color: #2b3a32 !important;
    }

    /* 3. 各級標題字體加大與綠色系色彩 */
    h1 {
        font-size: 2.3rem !important;
        font-weight: 700 !important;
        color: #1b4332 !important;
        padding-bottom: 0.5rem;
    }
    h2 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #2d6a4f !important;
        margin-top: 1rem !important;
    }
    h3 {
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        color: #40916c !important;
    }

    /* 4. 左側側邊欄清新風格 */
    [data-testid="stSidebar"] {
        background-color: #e8f3ed !important;
        border-right: 1px solid #d3e5db;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.6rem !important;
        color: #1b4332 !important;
    }

    /* 5. 表格 (DataFrame) 字體加大與圓角陰影 */
    .stDataFrame {
        font-size: 1.15rem !important;
        background-color: #ffffff;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    /* 6. 按鈕清新綠色系與大字體 */
    .stButton > button {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        background-color: #52b788 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.8rem !important;
        border: none !important;
        box-shadow: 0 3px 8px rgba(82, 183, 136, 0.3) !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #40916c !important;
        color: white !important;
        transform: translateY(-2px);
    }

    /* 7. 表單與輸入框加大 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[role="button"] {
        font-size: 1.15rem !important;
        border-radius: 8px !important;
        border: 1px solid #b7e4c7 !important;
        background-color: #ffffff !important;
    }

    /* 8. 下載按鈕特別樣式 */
    .stDownloadButton > button {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        background-color: #2d6a4f !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.8rem !important;
    }

    /* 9. 提示框 (Alert) 加大 */
    .stAlert {
        font-size: 1.15rem !important;
        border-radius: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 🔗 Google 試算表設定與 Direct CSV 讀取機制
# ==============================================================================
SHEET_ID = "12gjsQ8Zh3Ozf4_k9tFn_r2XMj4EEOFXwo2NppOhrZ90"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(sheet_name, expected_cols):
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(csv_url)
        if df is None or df.empty:
            return pd.DataFrame(columns=expected_cols)
        
        # 🧹 自動剔除多餘的 Unnamed 欄位與全空白資料列
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        st.warning(f"⚠️ 無法讀取分頁 [{sheet_name}]：{e}")
        return pd.DataFrame(columns=expected_cols)

def save_sheet(sheet_name, df):
    try:
        conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)
    except Exception as e:
        st.error(f"❌ 雲端更新失敗（請檢查 Streamlit Secrets 設定）：{e}")

# 載入資料
df_items = load_sheet("items", ["品名", "單位", "總庫存", "安全庫存"])
df_trans = load_sheet("transactions", ["日期", "品名", "異動類型", "數量", "備註"])
df_expiry = load_sheet("expiry", ["品名", "到期年月", "數量"])

# ==============================================================================
# 📌 側邊欄選單
# ==============================================================================
st.sidebar.title("🏥 衛保組衛材管理")
menu = st.sidebar.radio("📌 功能選單", ["📊 庫存儀表板", "📥 入庫與領用", "📋 月盤點作業", "📈 月報表與匯出"])

# ==============================================================================
# 1. 📊 庫存儀表板
# ==============================================================================
if menu == "📊 庫存儀表板":
    st.title("📊 庫存與預警儀表板")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ 低庫存預警 (低於安全庫存)")
        if not df_items.empty and '總庫存' in df_items.columns and '安全庫存' in df_items.columns:
            low_stock = df_items[pd.to_numeric(df_items['總庫存'], errors='coerce') <= pd.to_numeric(df_items['安全庫存'], errors='coerce')]
            if not low_stock.empty:
                st.error("以下品項需要盡快採購！")
                st.dataframe(low_stock, hide_index=True, use_container_width=True)
            else:
                st.success("✅ 目前所有衛材庫存充足。")
        else:
            st.info("尚無衛材資料，請前往「入庫與領用」新增品項。")

    with col2:
        st.subheader("⏰ 效期預警 (未來半年內到期)")
        if not df_expiry.empty and '到期年月' in df_expiry.columns:
            now = datetime.now()
            six_months_later = now + timedelta(days=180)
            target_ym = int(six_months_later.strftime("%Y%m"))
            df_expiry['到期年月_整數'] = pd.to_numeric(df_expiry['到期年月'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce')
            near_expiry = df_expiry[(df_expiry['到期年月_整數'] <= target_ym) & (pd.to_numeric(df_expiry['數量'], errors='coerce') > 0)]
            if not near_expiry.empty:
                st.warning("以下批次即將到期，請優先排入使用！")
                st.dataframe(near_expiry[['品名', '到期年月', '數量']], hide_index=True, use_container_width=True)
            else:
                st.success("✅ 目前無近期到期之衛材。")

    st.markdown("---")
    st.subheader("📦 目前所有衛材清單")
    st.dataframe(df_items, hide_index=True, use_container_width=True)

# ==============================================================================
# 2. 📥 入庫與領用 (含效期登記功能)
# ==============================================================================
elif menu == "📥 入庫與領用":
    st.title("📥 日常入庫與領用登記")
    item_list = df_items['品名'].dropna().tolist() if not df_items.empty and '品名' in df_items.columns else []
    
    st.subheader("➕ 新增 / 異動衛材紀錄")
    with st.form("transaction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            t_date = st.date_input("登記日期", datetime.now())
            t_item = st.selectbox("品名 (若無請選擇建立新品項)", item_list + ["新建品項..."]) if item_list else "新建品項..."
            if t_item == "新建品項...":
                new_item_name = st.text_input("輸入新品名")
                new_item_unit = st.text_input("單位 (如: 包, 盒, 個)", value="個")
                new_item_safe = st.number_input("安全庫存量", min_value=1, value=10)
        
        with col2:
            t_type = st.selectbox("異動類型", ["採購入庫", "領用 (出庫)"])
            t_qty = st.number_input("數量", min_value=1, step=1)
            # 📅 新增有效日期選擇器（預設一年後）
            t_expiry_date = st.date_input("衛材有效日期 / 到期日 (採購入庫時填寫)", datetime.now() + timedelta(days=365))
        
        with col3:
            t_note = st.text_input("備註 (領用事由或採購批號)")
        
        submit = st.form_submit_button("送出並儲存至雲端")
        
        if submit:
            target_name = new_item_name if (t_item == "新建品項..." or not item_list) else t_item
            
            # 1. 更新現有庫存總表 (items)
            if t_item == "新建品項..." or not item_list:
                new_item_row = pd.DataFrame([{"品名": target_name, "單位": new_item_unit, "總庫存": t_qty if t_type == "採購入庫" else 0, "安全庫存": new_item_safe}])
                df_items = pd.concat([df_items, new_item_row], ignore_index=True)
            else:
                idx = df_items.index[df_items['品名'] == target_name].tolist()[0]
                curr = int(df_items.at[idx, '總庫存'])
                df_items.at[idx, '總庫存'] = curr + t_qty if t_type == "採購入庫" else curr - t_qty

            # 2. 更新日常異動明細表 (transactions)
            new_trans = pd.DataFrame([{"日期": str(t_date), "品名": target_name, "異動類型": t_type, "數量": t_qty, "備註": t_note}])
            df_trans = pd.concat([df_trans, new_trans], ignore_index=True)
            
            # 3. 若為「採購入庫」，同步記錄到效期預警表 (expiry)
            if t_type == "採購入庫":
                exp_ym = t_expiry_date.strftime("%Y-%m")  # 格式如：2026-12
                new_expiry = pd.DataFrame([{"品名": target_name, "到期年月": exp_ym, "數量": t_qty}])
                df_expiry = pd.concat([df_expiry, new_expiry], ignore_index=True)
                save_sheet("expiry", df_expiry)

            # 儲存 items 與 transactions 雲端試算表
            save_sheet("items", df_items)
            save_sheet("transactions", df_trans)
            
            st.success(f"✅ 已成功更新雲端資料：{target_name} {t_type} {t_qty} 筆！")
            st.rerun()

# ==============================================================================
# 3. 📋 月盤點作業 (含數量與效期雙重校正)
# ==============================================================================
elif menu == "📋 月盤點作業":
    st.title("📋 月度盤點與庫存 / 效期校正")
    
    if not df_items.empty and '品名' in df_items.columns:
        item_to_check = st.selectbox("請選擇盤點品項", df_items['品名'].dropna().tolist())
        
        st.markdown("---")
        
        # ----------------------------------------------------------------------
        # 區塊 A：總庫存數量校正
        # ----------------------------------------------------------------------
        st.subheader("1. 📦 總庫存數量盤點")
        
        # 取得目前帳面庫存
        matched_item = df_items[df_items['品名'] == item_to_check]
        current_stock = int(matched_item['總庫存'].values[0]) if not matched_item.empty else 0
        
        st.write(f"目前雲端帳面庫存： **{current_stock}**")
        actual_stock = st.number_input("請輸入實際盤點數量", min_value=0, value=current_stock, step=1)
        
        if st.button("確認數量盤點校正"):
            diff = actual_stock - current_stock
            if diff != 0:
                t_type = "盤盈" if diff > 0 else "盤虧"
                new_trans = pd.DataFrame([{"日期": str(datetime.now().date()), "品名": item_to_check, "異動類型": f"盤點校正-{t_type}", "數量": abs(diff), "備註": "月盤點"}])
                df_trans = pd.concat([df_trans, new_trans], ignore_index=True)
                
                idx = df_items.index[df_items['品名'] == item_to_check].tolist()[0]
                df_items.at[idx, '總庫存'] = actual_stock
                
                save_sheet("items", df_items)
                save_sheet("transactions", df_trans)
                st.success(f"✅ 已校正雲端總庫存為：{actual_stock}")
                st.rerun()
            else:
                st.info("數量無異動，無需校正。")

        st.markdown("---")

        # ----------------------------------------------------------------------
        # 區塊 B：有效日期修正區
        # ----------------------------------------------------------------------
        st.subheader("2. 📅 衛材有效日期修正")
        
        # 篩選出該品項目前的效期紀錄
        item_expiry_df = df_expiry[df_expiry['品名'] == item_to_check] if not df_expiry.empty else pd.DataFrame()

        if not item_expiry_df.empty:
            st.write(f"目前 **{item_to_check}** 的雲端效期紀錄：")
            st.dataframe(item_expiry_df[['品名', '到期年月', '數量']], hide_index=True, use_container_width=True)
            
            with st.expander("✏️ 點此修正或更正錯誤的到期日", expanded=True):
                old_exp_list = item_expiry_df['到期年月'].astype(str).tolist()
                selected_old_exp = st.selectbox("選擇要更正的舊到期日", old_exp_list)
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    correct_date = st.date_input("修正後正確的到期日", datetime.now() + timedelta(days=365))
                with col_e2:
                    correct_qty = st.number_input("此批次數量", min_value=0, value=int(item_expiry_df[item_expiry_df['到期年月'].astype(str) == selected_old_exp]['數量'].values[0]))
                
                if st.button("儲存並更新效期"):
                    # 刪除舊的這筆效期紀錄，並寫入新的
                    df_expiry = df_expiry[~((df_expiry['品名'] == item_to_check) & (df_expiry['到期年月'].astype(str) == selected_old_exp))]
                    
                    new_exp_ym = correct_date.strftime("%Y-%m")
                    updated_row = pd.DataFrame([{"品名": item_to_check, "到期年月": new_exp_ym, "數量": correct_qty}])
                    df_expiry = pd.concat([df_expiry, updated_row], ignore_index=True)
                    
                    save_sheet("expiry", df_expiry)
                    st.success(f"✅ 已將【{item_to_check}】的效期由 {selected_old_exp} 更新為 {new_exp_ym}！")
                    st.rerun()
        else:
            st.info(f"目前此品項尚無效期紀錄。")
            with st.expander("➕ 為此品項補登效期紀錄"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    add_date = st.date_input("設定到期日", datetime.now() + timedelta(days=365))
                with col_e2:
                    add_qty = st.number_input("設定批次數量", min_value=1, value=current_stock)
                
                if st.button("補登效期"):
                    new_exp_ym = add_date.strftime("%Y-%m")
                    updated_row = pd.DataFrame([{"品名": item_to_check, "到期年月": new_exp_ym, "數量": add_qty}])
                    df_expiry = pd.concat([df_expiry, updated_row], ignore_index=True)
                    
                    save_sheet("expiry", df_expiry)
                    st.success(f"✅ 已成功補登【{item_to_check}】效期至 {new_exp_ym}！")
                    st.rerun()
                    
# ==============================================================================
# 4. 📈 月報表與學期報表匯出 (修正 1970-01 錯誤 & 支援學期統計表)
# ==============================================================================
elif menu == "📈 月報表與匯出":
    st.title("📈 衛材月報表與學期統計報表")
    
    # --------------------------------------------------------------------------
    # 🛠️ 日期強效修復邏輯 (解決 1970-01 問題)
    # --------------------------------------------------------------------------
    if not df_trans.empty and '日期' in df_trans.columns:
        # 清理日期中的符號，將 20260812, 2026-08-12, 2026/08/12 統一轉為 datetime
        clean_date = df_trans['日期'].astype(str).str.replace(r'[\-\/\s]', '', regex=True)
        df_trans['日期_dt'] = pd.to_datetime(clean_date, format='%Y%m%d', errors='coerce')
        
        # 備用修復 (針對其他無法直接轉換的格式)
        mask = df_trans['日期_dt'].isna()
        if mask.any():
            df_trans.loc[mask, '日期_dt'] = pd.to_datetime(df_trans.loc[mask, '日期'], errors='coerce')
            
        df_trans['年月'] = df_trans['日期_dt'].dt.strftime('%Y-%m')
        df_trans['年份'] = df_trans['日期_dt'].dt.year
        df_trans['月份'] = df_trans['日期_dt'].dt.month
    else:
        df_trans['日期_dt'] = pd.Series(dtype='datetime64[ns]')
        df_trans['年月'] = pd.Series(dtype='str')

    # 建立分頁頁籤：【月度明細】與【學期統計表】
    tab1, tab2 = st.tabs(["📅 月度異動明細", "🏫 學期衛材使用統計表 (如樣張)"])

    # --------------------------------------------------------------------------
    # TAB 1: 單月異動明細
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("📅 月度衛材異動明細")
        available_months = sorted(df_trans['年月'].dropna().unique(), reverse=True) if '年月' in df_trans.columns else []
        if not available_months or any(m.startswith("1970") for m in available_months):
            available_months = [datetime.now().strftime('%Y-%m')]

        selected_month = st.selectbox("請選擇欲檢視的月份", available_months, key="month_select")

        month_trans = df_trans[df_trans['年月'] == selected_month].drop(columns=['日期_dt', '年月', '年份', '月份'], errors='ignore') if not df_trans.empty else pd.DataFrame()

        st.dataframe(month_trans, hide_index=True, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 2: 學期衛材使用統計表 (樣張橫向交叉表)
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("🏫 學期衛材使用統計表")
        
        # 設定學期選擇器
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            semester_year = st.selectbox("選擇學年度", [114, 115, 116], index=0)
        with col_s2:
            semester_type = st.selectbox("選擇學期", ["第2學期 (2月 ~ 7月)", "第1學期 (8月 ~ 次年1月)"])

        # 計算西元年與月份範圍
        ad_year = semester_year + 1911
        if "第2學期" in semester_type:
            months_list = [(ad_year + 1, m) for m in [2, 3, 4, 5, 6, 7]]  # 例如 114學年第2學期 = 2026/02~2026/07
            semester_title = f"{semester_year}學年度第2學期學期衛材使用統計表"
        else:
            months_list = [(ad_year, m) for m in [8, 9, 10, 11, 12]] + [(ad_year + 1, 1)] # 8月~1月
            semester_title = f"{semester_year}學年度第1學期學期衛材使用統計表"

        st.markdown(f"### 📋 {semester_title}")

        # 構建統計表結構
        if not df_items.empty and '品名' in df_items.columns:
            semester_data = []
            
            # 整理效期字串對照 (品名 -> 有限期限/數量)
            expiry_summary = {}
            if not df_expiry.empty and '品名' in df_expiry.columns and '到期年月' in df_expiry.columns:
                for item_name, group in df_expiry.groupby('品名'):
                    exp_strs = []
                    for _, row in group.iterrows():
                        exp_ym = str(row['到期年月']).replace('-', '')
                        exp_qty = row['數量']
                        exp_strs.append(f"{exp_ym}/{exp_qty}")
                    expiry_summary[item_name] = "\n".join(exp_strs)

            for _, item_row in df_items.iterrows():
                p_name = item_row['品名']
                p_unit = item_row.get('單位', '個')
                
                row_dict = {"品名": p_name, "單位": p_unit}
                total_usage = 0
                
                # 計算各月的使用量與盤點量
                for y, m in months_list:
                    roc_m_label = f"{y-1911}/{m}"
                    
                    # 篩選該月份該品項的異動
                    m_trans = df_trans[(df_trans['年份'] == y) & (df_trans['月份'] == m) & (df_trans['品名'] == p_name)] if not df_trans.empty else pd.DataFrame()
                    
                    # 領用/出庫數量 (使用量)
                    usage = 0
                    if not m_trans.empty and '異動類型' in m_trans.columns:
                        usage_df = m_trans[m_trans['異動類型'].str.contains('領用|出庫', na=False)]
                        usage = pd.to_numeric(usage_df['數量'], errors='coerce').sum()
                    
                    total_usage += usage
                    
                    # 寫入欄位
                    row_dict[f"{roc_m_label} 使用量"] = int(usage)
                
                row_dict["總使用量"] = int(total_usage)
                row_dict["有限期限/數量"] = expiry_summary.get(p_name, "")
                
                semester_data.append(row_dict)

            df_semester = pd.DataFrame(semester_data)
            
            # 顯示表格
            st.dataframe(df_semester, hide_index=True, use_container_width=True)

            # Excel 匯出功能 (完美重現圖片格式)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_semester.to_excel(writer, sheet_name="學期衛材統計表", index=False)
            output.seek(0)

            st.download_button(
                label=f"📥 下載【{semester_title}】Excel 統計報表",
                data=output,
                file_name=f"{semester_title}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("目前尚無衛材清單資料。")
