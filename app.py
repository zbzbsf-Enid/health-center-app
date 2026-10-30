import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(
    page_title="北大衛保組 - 衛材全方位管理系統",
    page_icon="💊",
    layout="wide"
)

# 清新風格與 A4 橫向報表 CSS
custom_css = """
<style>
    :root {
        --primary-green: #1b5e20;
        --header-bg: #e8f5e9;
        --header-text: #1b5e20;
        --alt-row-bg: #fdfdfd;
        --border-color: #c8e6c9;
    }

    /* A4 報表通用容器 */
    .a4-container {
        background-color: #ffffff;
        width: 100%;
        max-width: 1150px;
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
        border-bottom: 2px solid var(--primary-green);
        padding-bottom: 10px;
    }
    .report-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--primary-green);
        letter-spacing: 1px;
    }
    .report-meta {
        font-size: 13px;
        color: #555555;
        margin-top: 6px;
        display: flex;
        justify-content: space-between;
    }

    /* 表格通用樣式 */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        color: #333333;
        margin-top: 10px;
    }
    .report-table th {
        background-color: var(--header-bg);
        color: var(--header-text);
        font-weight: 600;
        padding: 6px 3px;
        border: 1px solid var(--border-color);
        text-align: center;
        vertical-align: middle;
        white-space: pre-line;
    }
    .report-table td {
        padding: 5px 3px;
        border: 1px solid #e0e0e0;
        text-align: center;
        vertical-align: middle;
    }
    .report-table tr:nth-child(even) { background-color: var(--alt-row-bg); }
    .report-table tr:hover { background-color: #f1f8e9; }
    
    .text-left { text-align: left !important; padding-left: 6px !important; }
    .font-bold { font-weight: bold; }
    .bg-in { background-color: #e3f2fd !important; color: #1565c0; font-weight: bold; }
    .bg-out { background-color: #fff3e0 !important; color: #e65100; font-weight: bold; }
    .bg-waste { background-color: #ffebee !important; color: #c62828; font-weight: bold; }
    .bg-stock { background-color: #e8f5e9 !important; color: #1b5e20; font-weight: bold; }

    .sign-section {
        margin-top: 30px;
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #444;
        padding: 0 10px;
    }

    @media print {
        @page { size: A4 landscape; margin: 6mm; }
        section[data-testid="stSidebar"], .stButton, header, footer { display: none !important; }
        .a4-container { box-shadow: none !important; border: none !important; padding: 0 !important; width: 100% !important; max-width: none !important; }
    }
</style>
"""

# ==========================================
# 2. 全品項基礎資料與學期數據集
# ==========================================
all_items_data = [
    {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "月初庫存": 132, "本月購入": 24, "本月領用": 4, "過期報銷": 0, "盤點調整": 0, "月底結餘": 152, "有效期限/批號": "202802/1\n202909/3\n203003/4", "最近到期日": "2028-02-28", "狀態": "🟢 狀態正常", "p1": 132, "p2": 128, "u1": 4, "p3": 120, "u2": 8, "p4": 120, "u3": 0, "p5": 120, "u4": 0, "p6": 120, "u5": 0, "p7": 108, "u6": 1, "總使用量": 13},
    {"品名": "3M 1吋膠帶 (含切台)", "單位": "捲", "月初庫存": 26, "本月購入": 0, "本月領用": 0, "過期報銷": 1, "盤點調整": 0, "月底結餘": 25, "有效期限/批號": "20251127/25", "最近到期日": "2025-11-27", "狀態": "🔴 已過期 (需報銷)", "p1": 26, "p2": 26, "u1": 0, "p3": 26, "u2": 0, "p4": 26, "u3": 0, "p5": 26, "u4": 0, "p6": 26, "u5": 0, "p7": 25, "u6": 1, "總使用量": 1},
    {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "月初庫存": 55, "本月購入": 0, "本月領用": 4, "過期報銷": 0, "盤點調整": 0, "月底結餘": 51, "有效期限/批號": "20260321/11\n20300609/23", "最近到期日": "2026-03-21", "狀態": "🟠 即將到期", "p1": 55, "p2": 51, "u1": 4, "p3": 46, "u2": 5, "p4": 46, "u3": 0, "p5": 40, "u4": 6, "p6": 36, "u5": 4, "p7": 34, "u6": 2, "總使用量": 21},
    {"品名": "3吋棉棒 (10枝/包)", "單位": "包", "月初庫存": 115, "本月購入": 50, "本月領用": 5, "過期報銷": 0, "盤點調整": 0, "月底結餘": 160, "有效期限/批號": "20260815/85\n20281105/25", "最近到期日": "2026-08-15", "狀態": "🟢 狀態正常", "p1": 115, "p2": 110, "u1": 5, "p3": 110, "u2": 0, "p4": 110, "u3": 0, "p5": 110, "u4": 0, "p6": 110, "u5": 0, "p7": 110, "u6": 0, "總使用量": 5},
    {"品名": "沖洗棉棒 (5枝/包)", "單位": "包", "月初庫存": 400, "本月購入": 0, "本月領用": 100, "過期報銷": 10, "盤點調整": 0, "月底結餘": 290, "有效期限/批號": "20270911/100\n20280602/50", "最近到期日": "2027-09-11", "狀態": "🟢 狀態正常", "p1": 400, "p2": 300, "u1": 100, "p3": 250, "u2": 50, "p4": 250, "u3": 0, "p5": 250, "u4": 0, "p6": 225, "u5": 25, "p7": 200, "u6": 25, "總使用量": 200}
]
df_all = pd.DataFrame(all_items_data)

# ==========================================
# 3. 側邊欄與導覽
# ==========================================
st.sidebar.title("💊 衛材進銷存系統")
menu = st.sidebar.radio(
    "功能選單",
    (
        "⏰ 效期預警與全品項清單", 
        "📊 月度衛材進銷存報表",
        "📋 學期衛材統計大表 (A4)", 
        "📝 每日/每月異動登記"
    ),
    index=0
)

# ==========================================
# 4. 功能 1：⏰ 效期預警與全品項清單
# ==========================================
if menu == "⏰ 效期預警與全品項清單":
    st.title("⏰ 衛材全品項有效期限追蹤與報銷清單")
    
    expired_count = len(df_all[df_all['狀態'].str.contains('已過期')])
    warning_count = len(df_all[df_all['狀態'].str.contains('即將到期')])
    normal_count = len(df_all[df_all['狀態'].str.contains('正常')])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 總監控品項", f"{len(df_all)} 項")
    c2.metric("🔴 已過期 (需報銷)", f"{expired_count} 項")
    c3.metric("🟠 即將到期 (預警)", f"{warning_count} 項")
    c4.metric("🟢 效期正常", f"{normal_count} 項")

    st.markdown("---")
    filter_status = st.multiselect(
        "🔍 依狀態篩選檢視：", 
        ["🔴 已過期 (需報銷)", "🟠 即將到期", "🟢 狀態正常"],
        default=["🔴 已過期 (需報銷)", "🟠 即將到期", "🟢 狀態正常"]
    )
    filtered_df = df_all[df_all['狀態'].isin(filter_status)] if filter_status else df_all
    st.dataframe(filtered_df[['品名', '單位', '月底結餘', '最近到期日', '有效期限/批號', '狀態']], use_container_width=True, hide_index=True)

# ==========================================
# 5. 功能 2：📊 月度衛材進銷存報表
# ==========================================
elif menu == "📊 月度衛材進銷存報表":
    st.title("📊 月度衛材進銷存與報銷統計表")
    col_y, col_m = st.columns([1, 1])
    with col_y:
        selected_year = st.selectbox("選擇年份", ["115年 (2026)", "114年 (2025)"], index=0)
    with col_m:
        selected_month = st.selectbox("選擇月份", [f"{m}月" for m in range(1, 13)], index=1)

    table_rows = ""
    for _, row in df_all.iterrows():
        expiry_fmt = str(row['有效期限/批號']).replace('\n', '<br>')
        table_rows += f"""
        <tr>
            <td class="text-left font-bold">{row['品名']}</td>
            <td>{row['單位']}</td>
            <td>{row['月初庫存']}</td>
            <td class="bg-in">+{row['本月購入']}</td>
            <td class="bg-out">-{row['本月領用']}</td>
            <td class="bg-waste">-{row['過期報銷']}</td>
            <td>{row['盤點調整']}</td>
            <td class="bg-stock">{row['月底結餘']}</td>
            <td class="text-left" style="font-size: 10px; line-height: 1.2;">{expiry_fmt}</td>
        </tr>
        """

    full_html = f"""
    {custom_css}
    <div class="a4-container">
        <div class="report-header">
            <div class="report-title">國立臺北大學衛生保健組 衛材進銷存月報表</div>
            <div class="report-meta">
                <span><b>統計月份：</b>{selected_year} {selected_month}</span>
                <span><b>製表日期：</b>{datetime.date.today().strftime('%Y年%m月%d日')}</span>
            </div>
        </div>
        <table class="report-table">
            <thead>
                <tr>
                    <th style="width: 22%;">衛材品名 (規格)</th>
                    <th style="width: 5%;">單位</th>
                    <th style="width: 9%;">月初庫存</th>
                    <th style="width: 9%; background-color: #bbdefb; color: #0d47a1;">本月購入</th>
                    <th style="width: 9%; background-color: #ffe0b2; color: #e65100;">本月領用</th>
                    <th style="width: 9%; background-color: #ffcdd2; color: #b71c1c;">過期報銷</th>
                    <th style="width: 8%;">盤點調整</th>
                    <th style="width: 9%; background-color: #c8e6c9; color: #1b5e20;">月底結餘</th>
                    <th style="width: 20%;">有效期限 / 批號數量</th>
                </tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
        <div class="sign-section">
            <div>經手人/護理師：__________________</div>
            <div>衛保組組長：__________________</div>
        </div>
    </div>
    """
    st.html(full_html)

# ==========================================
# 6. 功能 3：📋 學期衛材統計大表 (A4 自動彙整)
# ==========================================
elif menu == "📋 學期衛材統計大表 (A4)":
    st.title("📋 學期衛材使用統計庫存大表")

    col_sel1, col_sel2 = st.columns([1, 1])
    with col_sel1:
        academic_year = st.selectbox("選擇學年度", ["114", "115", "116"], index=1)
    with col_sel2:
        semester = st.selectbox("選擇學期", ["第1學期 (8月~次年1月)", "第2學期 (2月~7月)"], index=0)

    ay_int = int(academic_year)
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

    sem_table_rows = ""
    for _, row in df_all.iterrows():
        expiry_fmt = str(row['有效期限/批號']).replace('\n', '<br>')
        sem_table_rows += f"""
        <tr>
            <td class="text-left font-bold">{row['品名']}</td>
            <td>{row['單位']}</td>
            <td>{row['p1']}</td><td>{row['p2']}</td><td>{row['u1']}</td>
            <td>{row['p3']}</td><td>{row['u2']}</td><td>{row['p4']}</td>
            <td>{row['u3']}</td><td>{row['p5']}</td><td>{row['u4']}</td>
            <td>{row['p6']}</td><td>{row['u5']}</td><td>{row['p7']}</td>
            <td>{row['u6']}</td>
            <td class="bg-stock">{row['總使用量']}</td>
            <td class="text-left" style="font-size: 10px; line-height: 1.2;">{expiry_fmt}</td>
        </tr>
        """

    sem_html = f"""
    {custom_css}
    <div class="a4-container">
        <div class="report-header">
            <div class="report-title">{academic_year}學年度{semester[:4]}學期衛材使用統計表</div>
            <div class="report-meta">
                <span><b>統計區間：</b>{subtitle_date}</span>
                <span><b>國立臺北大學衛生保健組</b></span>
            </div>
        </div>
        <table class="report-table">
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
            <tbody>{sem_table_rows}</tbody>
        </table>
        <div class="sign-section">
            <div>承辦人：__________________</div>
            <div>衛保組組長：__________________</div>
        </div>
    </div>
    """
    st.html(sem_html)

# ==========================================
# 7. 功能 4：📝 每日/每月異動登記
# ==========================================
elif menu == "📝 每日/每月異動登記":
    st.title("📝 衛材異動與報銷登記")
    with st.form("action_form"):
        c1, c2 = st.columns(2)
        with c1:
            rec_date = st.date_input("登記日期", datetime.date.today())
            item_name = st.selectbox("衛材品名", df_all['品名'].tolist())
            act_type = st.selectbox("異動類別", ["領用 (消耗)", "購入 (進貨)", "過期報銷", "盤點校正"])
        with c2:
            num = st.number_input("異動數量", min_value=1, value=1)
            batch = st.text_input("有效期限批號", placeholder="例如：202802/1")
            memo = st.text_input("備註原因", value="")
            
        if st.form_submit_button("💾 儲存紀錄"):
            st.success(f"✅ 已成功登記：{rec_date} | {item_name} | {act_type} {num}")
