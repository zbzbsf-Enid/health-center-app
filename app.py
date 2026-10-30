import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(
    page_title="北大衛保組 - 衛材每月進銷存與報銷管理系統",
    page_icon="🩹",
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

    /* A4 報表容器 (寬度調整至符合 9~10 欄位) */
    .a4-monthly-container {
        background-color: #ffffff;
        width: 100%;
        max-width: 1100px;
        margin: 0 auto;
        padding: 25px 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
    }

    .monthly-header {
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 2px solid var(--primary-green);
        padding-bottom: 10px;
    }
    .monthly-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--primary-green);
        letter-spacing: 1px;
    }
    .monthly-meta {
        font-size: 13px;
        color: #555555;
        margin-top: 6px;
        display: flex;
        justify-content: space-between;
    }

    /* 表格樣式 */
    .monthly-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11.5px;
        color: #333333;
        margin-top: 10px;
    }
    .monthly-table th {
        background-color: var(--header-bg);
        color: var(--header-text);
        font-weight: 600;
        padding: 8px 4px;
        border: 1px solid var(--border-color);
        text-align: center;
        vertical-align: middle;
        white-space: pre-line;
    }
    .monthly-table td {
        padding: 6px 4px;
        border: 1px solid #e0e0e0;
        text-align: center;
        vertical-align: middle;
    }
    .monthly-table tr:nth-child(even) { background-color: var(--alt-row-bg); }
    .monthly-table tr:hover { background-color: #f1f8e9; }
    
    /* 欄位色彩醒目化 */
    .text-left { text-align: left !important; padding-left: 6px !important; }
    .font-bold { font-weight: bold; }
    .bg-in { background-color: #e3f2fd !important; color: #1565c0; font-weight: bold; } /* 入庫/購入：淡藍 */
    .bg-out { background-color: #fff3e0 !important; color: #e65100; font-weight: bold; } /* 領用/消耗：淡橘 */
    .bg-waste { background-color: #ffebee !important; color: #c62828; font-weight: bold; } /* 報銷/過期：淡紅 */
    .bg-stock { background-color: #e8f5e9 !important; color: #1b5e20; font-weight: bold; } /* 結餘：淡綠 */

    .sign-section {
        margin-top: 35px;
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #444;
        padding: 0 10px;
    }

    @media print {
        @page { size: A4 landscape; margin: 8mm; }
        section[data-testid="stSidebar"], .stButton, header, footer { display: none !important; }
        .a4-monthly-container { box-shadow: none !important; border: none !important; padding: 0 !important; width: 100% !important; max-width: none !important; }
    }
</style>
"""

# ==========================================
# 2. 側邊欄與導覽
# ==========================================
st.sidebar.title("🩹 衛材進銷存系統")
menu = st.sidebar.radio(
    "功能選單",
    ("📊 月度衛材統計報表", "📝 每日/每月異動登記 (進出/報銷)", "⏰ 效期預警與報銷清單")
)

# 測試用包含「購入、消耗、報銷」的資料集
sample_materials = [
    {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "月初庫存": 132, "本月購入": 24, "本月領用": 4, "過期報銷": 0, "盤點調整": 0, "月底結餘": 152, "有效期限/批號": "202802/1\n202909/3\n203003/4"},
    {"品名": "3M 1吋膠帶 (含切台)", "單位": "捲", "月初庫存": 26, "本月購入": 0, "本月領用": 0, "過期報銷": 1, "盤點調整": 0, "月底結餘": 25, "有效期限/批號": "20251127/25 (已清查)"},
    {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "月初庫存": 55, "本月購入": 0, "本月領用": 4, "過期報銷": 0, "盤點調整": 0, "月底結餘": 51, "有效期限/批號": "20260321/11\n20300609/23"},
    {"品名": "3吋棉棒 (10枝/包)", "單位": "包", "月初庫存": 115, "本月購入": 50, "本月領用": 5, "過期報銷": 0, "盤點調整": 0, "月底結餘": 160, "有效期限/批號": "20260815/85\n20281105/25"},
    {"品名": "沖洗棉棒 (5枝/包)", "單位": "包", "月初庫存": 400, "本月購入": 0, "本月領用": 100, "過期報銷": 10, "盤點調整": 0, "月底結餘": 290, "有效期限/批號": "20270911/100\n20280602/50"}
]
df_monthly = pd.DataFrame(sample_materials)

# ==========================================
# 3. 模組一：月度衛材統計報表
# ==========================================
if menu == "📊 月度衛材統計報表":
    st.title("📊 月度衛材進銷存與報銷統計表")

    col_y, col_m = st.columns([1, 1])
    with col_y:
        selected_year = st.selectbox("選擇年份", ["115年 (2026)", "114年 (2025)"], index=0)
    with col_m:
        selected_month = st.selectbox("選擇月份", [f"{m}月" for m in range(1, 13)], index=1)

    table_rows = ""
    for _, row in df_monthly.iterrows():
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
    <div class="a4-monthly-container">
        <div class="monthly-header">
            <div class="monthly-title">國立臺北大學衛生保健組 衛材進銷存與消耗報銷月報表</div>
            <div class="monthly-meta">
                <span><b>統計月份：</b>{selected_year} {selected_month}</span>
                <span><b>製表日期：</b>{datetime.date.today().strftime('%Y年%m月%d日')}</span>
            </div>
        </div>
        
        <table class="monthly-table">
            <thead>
                <tr>
                    <th style="width: 22%;">衛材品名 (規格)</th>
                    <th style="width: 5%;">單位</th>
                    <th style="width: 9%;">月初庫存</th>
                    <th style="width: 9%; background-color: #bbdefb; color: #0d47a1;">本月購入<br>(進貨)</th>
                    <th style="width: 9%; background-color: #ffe0b2; color: #e65100;">本月領用<br>(消耗)</th>
                    <th style="width: 9%; background-color: #ffcdd2; color: #b71c1c;">過期報銷<br>(損耗)</th>
                    <th style="width: 8%;">盤點調整</th>
                    <th style="width: 9%; background-color: #c8e6c9; color: #1b5e20;">月底結餘</th>
                    <th style="width: 20%;">有效期限 / 批號數量</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <div class="sign-section">
            <div>經手人/護理師：__________________</div>
            <div>衛保組組長：__________________</div>
        </div>
    </div>
    """

    st.html(full_html)

    st.markdown("<br>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        csv_bytes = df_monthly.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 下載 {selected_month} 衛材進銷存與報銷月報表 (CSV/Excel)",
            data=csv_bytes,
            file_name=f"{selected_year}_{selected_month}_衛材進銷存報表.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_d2:
        st.info("💡 **A4 列印提示**：按下 `Ctrl + P` (Mac 為 `Cmd + P`)，目標選擇「另存為 PDF」，方向選「橫向」即可呈現完整的進銷存表格。")

# ==========================================
# 4. 模組二：每日/每月異動登記
# ==========================================
elif menu == "📝 每日/每月異動登記 (進出/報銷)":
    st.title("📝 衛材異動與報銷登記")
    with st.form("action_entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            record_date = st.date_input("登記日期", datetime.date.today())
            mat_name = st.selectbox("選擇衛材", df_monthly['品名'].tolist())
            action_type = st.selectbox("異動類型", ["領用 (一般消耗)", "購入 (新進採購)", "過期報銷 (破損/到期廢棄)", "盤點校正"])
        with col2:
            qty = st.number_input("異動數量", min_value=1, value=1)
            batch_str = st.text_input("對應有效期限/批號", placeholder="例如：20260321/11")
            note = st.text_input("備註原因 (例如：過期報廢、廠商送達)", value="")
            
        btn = st.form_submit_button("💾 儲存紀錄")
        if btn:
            st.success(f"✅ 已成功登記：{record_date} | {mat_name} | {action_type}：{qty}")

# ==========================================
# 5. 模組三：效期預警與報銷
# ==========================================
elif menu == "⏰ 效期預警與報銷清單":
    st.title("⏰ 衛材有效期限追蹤與預判報銷")
    st.info("以下為即將到期（預警）與建議報銷之衛材項目：")
    
    sample_exp = [
        {"品名": "3M 1吋膠帶 (含切台)", "批號/數量": "20251127/25", "到期日": "2025-11-27", "目前數量": 25, "狀態": "🔴 已過期 (需報銷)"},
        {"品名": "3M彈繃3吋 (捲)", "批號/數量": "20260321/11", "到期日": "2026-03-21", "目前數量": 11, "狀態": "🟠 30天內到期"},
        {"品名": "3吋棉棒 (10枝/包)", "批號/數量": "20260815/85", "到期日": "2026-08-15", "目前數量": 85, "狀態": "🟢 狀態正常"},
    ]
    st.dataframe(pd.DataFrame(sample_exp), use_container_width=True, hide_index=True)
