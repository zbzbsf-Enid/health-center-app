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

# 清新風格與 A4 報表 CSS 樣式
custom_css = """
<style>
    :root {
        --primary-green: #1b5e20;
        --header-bg: #e8f5e9;
        --header-text: #1b5e20;
        --alt-row-bg: #fdfdfd;
        --border-color: #c8e6c9;
    }

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
# 2. 初始化 Session State (全 61 項衛材資料，已修復括號)
# ==========================================
if 'items_dataset' not in st.session_state:
    st.session_state.items_dataset = [
        {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "p1": 132, "p2": 128, "u1": 4, "p3": 120, "u2": 8, "p4": 120, "u3": 0, "p5": 120, "u4": 0, "p6": 120, "u5": 0, "p7": 108, "u6": 1, "總使用量": 13, "有限期限/數量": "202802/1\n202909/3\n203003/4"},
        {"品名": "3M 1吋膠帶 (含切台)", "單位": "捲", "p1": 26, "p2": 26, "u1": 0, "p3": 26, "u2": 0, "p4": 26, "u3": 0, "p5": 26, "u4": 0, "p6": 26, "u5": 0, "p7": 25, "u6": 1, "總使用量": 1, "有限期限/數量": "20251127/25"},
        {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "p1": 55, "p2": 51, "u1": 4, "p3": 46, "u2": 5, "p4": 46, "u3": 0, "p5": 40, "u4": 6, "p6": 36, "u5": 4, "p7": 34, "u6": 2, "總使用量": 21, "有限期限/數量": "20260321/11\n20300609/23"},
        {"品名": "3吋棉棒 （10枝/包）", "單位": "包", "p1": 115, "p2": 110, "u1": 5, "p3": 110, "u2": 0, "p4": 110, "u3": 0, "p5": 110, "u4": 0, "p6": 110, "u5": 0, "p7": 110, "u6": 0, "總使用量": 5, "有限期限/數量": "20260815/85\n20281105/25"},
        {"品名": "ENT棉棒(10包)", "單位": "包", "p1": 19, "p2": 19, "u1": 0, "p3": 19, "u2": 0, "p4": 19, "u3": 0, "p5": 17, "u4": 2, "p6": 10, "u5": 7, "p7": 5, "u6": 2, "總使用量": 11, "有限期限/數量": "20260927/19"},
        {"品名": "口腔棉棒 (10枝/包)", "單位": "包", "p1": 730, "p2": 700, "u1": 30, "p3": 680, "u2": 20, "p4": 680, "u3": 0, "p5": 660, "u4": 20, "p6": 640, "u5": 20, "p7": 600, "u6": 40, "總使用量": 130, "有限期限/數量": "20270705/100\n20280826/500"},
        {"品名": "普通棉棒 (10枝/包)", "單位": "包", "p1": 320, "p2": 300, "u1": 20, "p3": 280, "u2": 20, "p4": 270, "u3": 10, "p5": 260, "u4": 10, "p6": 220, "u5": 40, "p7": 83, "u6": 137, "總使用量": 237, "有限期限/數量": "20280806/83"},
        {"品名": "沖洗棉棒 (5枝/包)", "單位": "包", "p1": 400, "p2": 300, "u1": 100, "p3": 250, "u2": 50, "p4": 250, "u3": 0, "p5": 250, "u4": 0, "p6": 225, "u5": 25, "p7": 200, "u6": 25, "總使用量": 200, "有限期限/數量": "20270911/100\n20280602/50\n20280503/50"},
        {"品名": "優碘 (30ml/瓶)", "單位": "瓶", "p1": 19, "p2": 18, "u1": 1, "p3": 18, "u2": 0, "p4": 18, "u3": 0, "p5": 0, "u4": 18, "p6": 0, "u5": 0, "p7": 0, "u6": 0, "總使用量": 19, "有限期限/數量": "-"},
        {"品名": "優碘 200ml/瓶", "單位": "瓶", "p1": 2, "p2": 2, "u1": 0, "p3": 2, "u2": 0, "p4": 2, "u3": 0, "p5": 2, "u4": 0, "p6": 0, "u5": 2, "p7": 0, "u6": 0, "總使用量": 2, "有限期限/數量": "-"},
        {"品名": "綠油精", "單位": "瓶", "p1": 14, "p2": 0, "u1": 14, "p3": 0, "u2": 0, "p4": 0, "u3": 0, "p5": 0, "u4": 0, "p6": 0, "u5": 0, "p7": 0, "u6": 0, "總使用量": 14, "有限期限/數量": "-"},
        {"品名": "歐斯淨氧氣隨身瓶", "單位": "瓶", "p1": 5, "p2": 4, "u1": 1, "p3": 4, "u2": 0, "p4": 4, "u3": 0, "p5": 4, "u4": 0, "p6": 4, "u5": 0, "p7": 4, "u6": 0, "總使用量": 1, "有限期限/數量": "202704/4"},
        {"品名": "軟式護木 (手/小腿)", "單位": "個", "p1": 6, "p2": 6, "u1": 0, "p3": 6, "u2": 0, "p4": 6, "u3": 0, "p5": 6, "u4": 0, "p6": 6, "u5": 0, "p7": 6, "u6": 0, "總使用量": 0, "有限期限/數量": "-"},
        {"品名": "軟式護木 (大腿)", "單位": "個", "p1": 1, "p2": 1, "u1": 0, "p3": 1, "u2": 0, "p4": 1, "u3": 0, "p5": 1, "u4": 0, "p6": 1, "u5": 0,
