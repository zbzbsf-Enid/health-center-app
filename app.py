import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(
    page_title="學期衛材使用統計表 - 北大衛保組",
    page_icon="📋",
    layout="wide"
)

# ==========================================
# 2. 清新風格與 A4 橫向 (Landscape) CSS 樣式
# ==========================================
custom_css = """
<style>
    :root {
        --primary-green: #1b5e20;
        --header-bg: #e8f5e9;
        --header-text: #1b5e20;
        --alt-row-bg: #f9fbf9;
        --border-color: #c8e6c9;
    }

    /* A4 橫向報表容器 */
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

    /* 報表抬頭 */
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

    /* 學期統計大表樣式 */
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
    .semester-table tr:nth-child(even) {
        background-color: var(--alt-row-bg);
    }
    .semester-table tr:hover {
        background-color: #f1f8e9;
    }
    .text-left { text-align: left !important; padding-left: 5px !important; }
    .font-bold { font-weight: bold; }
    .highlight-usage { 
        background-color: #e8f5e9 !important; 
        font-weight: bold; 
        color: #1b5e20; 
    }

    /* A4 橫向列印設定 (Ctrl + P) */
    @media print {
        @page {
            size: A4 landscape;
            margin: 6mm;
        }
        section[data-testid="stSidebar"], 
        .stButton, 
        header, 
        footer {
            display: none !important;
        }
        .a4-landscape-container {
            box-shadow: none !important;
            border: none !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: none !important;
        }
    }
</style>
"""

# ==========================================
# 3. 頁面控制選單 (在這裡取得變數)
# ==========================================
st.title("📋 學期衛材統計庫存報表")

col_sel1, col_sel2 = st.columns([1, 1])
with col_sel1:
    academic_year = st.selectbox("選擇學年度", ["114", "115", "116"], index=1)
with col_sel2:
    semester = st.selectbox("選擇學期", ["第1學期 (8月~次年1月)", "第2學期 (2月~7月)"], index=0)

# ==========================================
# 4. 動態計算學年度、統計區間與表頭月份
# ==========================================
try:
    ay_int = int(str(academic_year).strip())
except ValueError:
    ay_int = 115

if "第2學期" in semester:
    # 第2學期：115年2月 ~ 115年7月 (年份 = 學年度 + 1)
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
    # 第1學期：115年8月 ~ 116年1月 (年份 = 學年度 ～ 學年度 + 1)
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

# ==========================================
#
