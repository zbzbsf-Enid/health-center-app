import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(
    page_title="北大衛保組 - 全方位衛材與效期管理系統",
    page_icon="🩹",
    layout="wide"
)

# A4 橫向報表 CSS 樣式
custom_css = """
<style>
    :root {
        --primary-green: #1b5e20;
        --header-bg: #e8f5e9;
        --header-text: #1b5e20;
        --alt-row-bg: #f9fbf9;
        --border-color: #c8e6c9;
    }

    .a4-landscape-container {
        background-color: #ffffff;
        width: 100%;
        max-width: 1180px;
        margin: 0 auto;
        padding: 25px 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
    }

    .report-header {
        text-align: center;
        margin-bottom: 20px;
    }
    .report-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--primary-green);
        letter-spacing: 1px;
    }
    .report-subtitle {
        font-size: 13px;
        color: #555555;
        margin-top: 4px;
    }

    .semester-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        color: #333333;
        margin-top: 10px;
    }
    .semester-table th {
        background-color: var(--header-bg);
        color: var(--header-text);
        font-weight: 600;
        padding: 6px 3px;
        border: 1px solid var(--border-color);
        text-align: center;
        vertical-align: middle;
        white-space: pre-line;
    }
    .semester-table td {
        padding: 5px 3px;
        border: 1px solid #e0e0e0;
        text-align: center;
        vertical-align: middle;
    }
    .semester-table tr:nth-child(even) { background-color: var(--alt-row-bg); }
    .semester-table tr:hover { background-color: #f1f8e9; }
    .text-left { text-align: left !important; padding-left: 5px !important; }
    .font-bold { font-weight: bold; }
    .highlight-usage { background-color: #e8f5e9 !important; font-weight: bold; color: #1b5e20; }

    @media print {
        @page { size: A4 landscape; margin: 6mm; }
        section[data-testid="stSidebar"], .stButton, header, footer { display: none !important; }
        .a4-landscape-container { box-shadow: none !important; border: none !important; padding: 0 !important; width: 100% !important; max-width: none !important; }
    }
</style>
"""

# ==========================================
# 2. 側邊欄與導覽
# ==========================================
st.sidebar.title("🩹 衛材管理系統")
menu = st.sidebar.radio(
    "功能模組",
    ("📌 系統儀表板 (效期警示)", "📥 每日進出量登記", "📋 學期統計報表 (A4)")
)

# 測試用資料 (未來對接 Google Sheets CSV)
sample_info = pd.DataFrame([
    {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "安全庫存": 20},
    {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "安全庫存": 15},
    {"品名": "沖洗棉棒 (5枝/包)", "單位": "包", "安全庫存": 50}
])

sample_batches = pd.DataFrame([
    {"品名": "3M 1吋膠帶 (12捲/盒)", "有效期限": "2028-02-28", "批號說明": "202802/1", "數量": 1},
    {"品名": "3M 1吋膠帶 (12捲/盒)", "有效期限": "2029-09-30", "批號說明": "202909/3", "數量": 3},
    {"品名": "3M 1吋膠帶 (12捲/盒)", "有效期限": "2030-03-31", "批號說明": "203003/4", "數量": 4},
    {"品名": "3M彈繃3吋 (捲)", "有效期限": "2026-03-21", "批號說明": "20260321/11", "數量": 11},
    {"品名": "3M彈繃3吋 (捲)", "有效期限": "2030-06-09", "批號說明": "20300609/23", "數量": 23}
])

# ==========================================
# 3. 模組一：系統儀表板 (效期警示)
# ==========================================
if menu == "📌 系統儀表板 (效期警示)":
    st.title("📌 衛材狀態與有效期限管理")
    
    # 計算近到期衛材 (例如 180 天內到期)
    sample_batches['有效期限_dt'] = pd.to_datetime(sample_batches['有效期限'])
    today = pd.to_datetime(datetime.date.today())
    expiring_soon = sample_batches[(sample_batches['有效期限_dt'] - today).dt.days <= 180]
    
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.metric("📦 衛材品項總數", len(sample_info))
    with col_kpi2:
        st.metric("⚠️ 近 180 天即將到期品項", len(expiring_soon))
        
    if not expiring_soon.empty:
        st.error("⚠️ **即將到期衛材警示列表**")
        st.dataframe(expiring_soon[['品名', '批號說明', '有效期限', '數量']], use_container_width=True, hide_index=True)
    else:
        st.success("🎉 目前無即將到期之衛材。")

# ==========================================
# 4. 模組二：每日進出量登記
# ==========================================
elif menu == "📥 每日進出量登記":
    st.title("📥 衛材進出量登記 (領用 / 入庫)")
    
    with st.form("trans_form"):
        col1, col2 = st.columns(2)
        with col1:
            trans_date = st.date_input("異動日期", datetime.date.today())
            material_selected = st.selectbox("選擇衛材", sample_info['品名'].tolist())
            trans_type = st.selectbox("異動類型", ["領用 (出庫)", "進貨 (入庫)", "盤點調整"])
        with col2:
            quantity = st.number_input("異動數量", min_value=1, value=1)
            handler = st.text_input("經手人 / 領用單位", value="衛保組")
            note = st.text_input("備註", value="")
            
        submitted = st.form_submit_dict = st.form_submit_button("💾 儲存異動紀錄")
        if submitted:
            st.success(f"✅ 已成功登記：{trans_date} | {material_selected} | {trans_type} {quantity} {sample_info[sample_info['品名']==material_selected]['單位'].values[0]}")

# ==========================================
# 5. 模組三：學期統計報表 (A4)
# ==========================================
elif menu == "📋 學期統計報表 (A4)":
    st.title("📋 學期衛材統計庫存報表")

    col_sel1, col_sel2 = st.columns([1, 1])
    with col_sel1:
        academic_year = st.selectbox("選擇學年度", ["114", "115", "116"], index=1)
    with col_sel2:
        semester = st.selectbox("選擇學期", ["第1學期 (8月~次年1月)", "第2學期 (2月~7月)"], index=0)

    # 動態計算學年度與表頭
    try:
        ay_int = int(str(academic_year).strip())
    except:
        ay_int = 115

    if "第2學期" in semester:
        start_year = ay_int + 1
        end_year = ay_int + 1
        subtitle_date = f"{start_year}年2月 ～ {end_year}年7月"
        m_headers = [
            f"{start_year}/2<br>盤點", f"{start_year}/3<br>盤點", f"{start_year}/2<br>使用",
            f"{start_year}/4<br>盤點", f"{start_year}/3<br>使用", f"{start_year}/5<br>盤點",
            f"{start_year}/4<br>使用", f"{start_year}/6<br>盤點", f"{start_year}/5<br>使用",
            f"{start_year}/7<br>盤點", f"{start_year}/6<br>使用", f"{start_year}/8<br>盤點",
            f"{start_year}/7<br>使用"
        ]
    else:
        start_year = ay_int
        end_year = ay_int + 1
        subtitle_date = f"{start_year}年8月 ～ {end_year}年1月"
        m_headers = [
            f"{start_year}/8<br>盤點", f"{start_year}/9<br>盤點", f"{start_year}/8<br>使用",
            f"{start_year}/10<br>盤點", f"{start_year}/9<br>使用", f"{start_year}/11<br>盤點",
            f"{start_year}/10<br>使用", f"{start_year}/12<br>盤點", f"{start_year}/11<br>使用",
            f"{end_year}/1<br>盤點", f"{start_year}/12<br>使用", f"{end_year}/2<br>盤點",
            f"{end_year}/1<br>使用"
        ]

    # 學期統計模擬數據
    sample_semester_data = [
        {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "p1": 132, "p2": 128, "u1": 4, "p3": 120, "u2": 8, "p4": 120, "u3": 0, "p5": 120, "u4": 0, "p6": 120, "u5": 0, "p7": 108, "u6": 1, "總使用量": 13, "有效期限/數量": "202802/1\n202909/3\n203003/4"},
        {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "p1": 55, "p2": 51, "u1": 4, "p3": 46, "u2": 5, "p4": 46, "u3": 0, "p5": 40, "u4": 6, "p6": 36, "u5": 4, "p7": 34, "u6": 2, "總使用量": 21, "有效期限/數量": "20260321/11\n20300609/23"}
    ]
    df_semester = pd.DataFrame(sample_semester_data)

    table_rows = ""
    for _, row in df_semester.iterrows():
        expiry_fmt = str(row['有效期限/數量']).replace('\n', '<br>')
        table_rows += f"""
        <tr>
            <td class="text-left font-bold">{row['品名']}</td>
            <td>{row['單位']}</td>
            <td>{row['p1']}</td><td>{row['p2']}</td><td>{row['u1']}</td>
            <td>{row['p3']}</td><td>{row['u2']}</td><td>{row['p4']}</td>
            <td>{row['u3']}</td><td>{row['p5']}</td><td>{row['u4']}</td>
            <td>{row['p6']}</td><td>{row['u5']}</td><td>{row['p7']}</td>
            <td>{row['u6']}</td>
            <td class="highlight-usage">{row['總使用量']}</td>
            <td class="text-left" style="font-size: 10px; line-height: 1.2;">{expiry_fmt}</td>
        </tr>
        """

    full_html = f"""
    {custom_css}
    <div class="a4-landscape-container">
        <div class="report-header">
            <div class="report-title">{academic_year}學年度{semester[:4]}學期衛材使用統計表</div>
            <div class="report-subtitle">國立臺北大學衛生保健組 ｜ 統計區間：{subtitle_date}</div>
        </div>
        <table class="semester-table">
            <thead>
                <tr>
                    <th style="width: 16%;">品名</th>
                    <th style="width: 4%;">單位</th>
                    <th>{m_headers[0]}</th><th>{m_headers[1]}</th><th>{m_headers[2]}</th>
                    <th>{m_headers[3]}</th><th>{m_headers[4]}</th><th>{m_headers[5]}</th>
                    <th>{m_headers[6]}</th><th>{m_headers[7]}</th><th>{m_headers[8]}</th>
                    <th>{m_headers[9]}</th><th>{m_headers[10]}</th><th>{m_headers[11]}</th>
                    <th>{m_headers[12]}</th>
                    <th style="background-color: #c8e6c9;">總使用量</th>
                    <th style="width: 14%;">有效期限/數量</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
    </div>
    """
    st.html(full_html)
