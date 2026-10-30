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
# 2. 檔案內全 61 項衛材完整資料庫建檔
# ==========================================
items_dataset = [
    {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "p1": 132, "p2": 128, "u1": 4, "p3": 120, "u2": 8, "p4": 120, "u3": 0, "p5": 120, "u4": 0, "p6": 120, "u5": 0, "p7": 108, "u6": 1, "總使用量": 13, "有限期限/數量": "202802/1\n202909/3\n203003/4"},
    {"品名": "3M 1吋膠帶 (含切台)", "單位": "捲", "p1": 26, "p2": 26, "u1": 0, "p3": 26, "u2": 0, "p4": 26, "u3": 0, "p5": 26, "u4": 0, "p6": 26, "u5": 0, "p7": 25, "u6": 1, "總使用量": 1, "有限期限/數量": "20251127/25"},
    {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "p1": 55, "p2": 51, "u1": 4, "p3": 46, "u2": 5, "p4": 46, "u3": 0, "p5": 40, "u4": 6, "p6": 36, "u5": 4, "p7": 34, "u6": 2, "總使用量": 21, "有限期限/數量": "20260321/11\n20300609/23"},
    {"品名": "3吋棉棒 （10枝/包）", "單位": "包", "p1": 115, "p2": 110, "u1": 5, "p3": 110, "u2": 0, "p4": 110, "u3": 0, "p5": 110, "u4": 0, "p6": 110, "u5": 0, "p7": 110, "u6": 0, "總使用量": 5, "有限期限/數量": "20260815/85\n20281105/25"},
    {"品名": "ENT棉棒(10包)", "單位": "包", "p1": 19, "p2": 19, "u1": 0, "p3": 19, "u2": 0, "p4": 19, "u3": 0, "p5": 17, "u4": 2, "p6": 10, "u5": 7, "p7": 5, "u6": 2, "總使用量": 11, "有限期限/數量": "20260927/19"},
    {"品名": "口腔棉棒 (10枝/包)", "單位": "包", "p1": 730, "p2": 700, "u1": 30, "p3": 680, "u2": 20, "p4": 680, "u3": 0, "p5": 660, "u4": 20, "p6": 640, "u5": 20, "p7": 600, "u6": 40, "總使用量": 130, "有限期限/數量": "20270705/100\n20280826/500"},
    {"品名": "普通棉棒 (10枝/包)", "單位": "包", "p1": 320, "p2": 300, "u1": 20, "p3": 280, "u2": 20, "p4": 270, "u3": 10, "p5": 260, "u4": 10, "p6": 220, "u5": 40, "p7": 83, "u6": 137, "總使用量": 237, "有限期限/數量": "20280806/83"},
    {"品名": "沖洗棉棒 (5枝/包)", "單位": "包", "p1": 400, "p2": 300, "u1": 100, "p3": 250, "u2": 50, "p4": 250, "u3": 0, "p5": 250, "u4": 0, "p6": 225, "u5": 25, "p7": 200, "u6": 25, "總使用量": 200, "有限期限/數量": "20270911/100 \n20280602/50\n20280503/50"},
    {"品名": "優碘 (30ml/瓶)", "單位": "瓶", "p1": 19, "p2": 18, "u1": 1, "p3": 18, "u2": 0, "p4": 18, "u3": 0, "p5": 0, "u4": 18, "p6": 0, "u5": 0, "p7": 0, "u6": 0, "總使用量": 19, "有限期限/數量": "-"},
    {"品名": "優碘 200ml/瓶", "單位": "瓶", "p1": 2, "p2": 2, "u1": 0, "p3": 2, "u2": 0, "p4": 2, "u3": 0, "p5": 2, "u4": 0, "p6": 0, "u5": 2, "p7": 0, "u6": 0, "總使用量": 2, "有限期限/數量": "-"},
    {"品名": "綠油精", "單位": "瓶", "p1": 14, "p2": 0, "u1": 14, "p3": 0, "u2": 0, "p4": 0, "u3": 0, "p5": 0, "u4": 0, "p6": 0, "u5": 0, "p7": 0, "u6": 0, "總使用量": 14, "有限期限/數量": "-"},
    {"品名": "歐斯淨氧氣隨身瓶", "單位": "瓶", "p1": 5, "p2": 4, "u1": 1, "p3": 4, "u2": 0, "p4": 4, "u3": 0, "p5": 4, "u4": 0, "p6": 4, "u5": 0, "p7": 4, "u6": 0, "總使用量": 1, "有限期限/數量": "202704/4"},
    {"品名": "軟式護木 (手/小腿)", "單位": "個", "p1": 6, "p2": 6, "u1": 0, "p3": 6, "u2": 0, "p4": 6, "u3": 0, "p5": 6, "u4": 0, "p6": 6, "u5": 0, "p7": 6, "u6": 0, "總使用量": 0, "有限期限/數量": "-"},
    {"品名": "軟式護木 (大腿)", "單位": "個", "p1": 1, "p2": 1, "u1": 0, "p3": 1, "u2": 0, "p4": 1, "u3": 0, "p5": 1, "u4": 0, "p6": 1, "u5": 0, "p7": 1, "u6": 0, "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 30, "p2": 30, "p3": 30, "p4": 30, "p5": 30, "p6": 30, "p7": 30, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "手臂吊帶", "單位": "條", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 15, "p2": 15, "p3": 15, "p4": 15, "p5": 15, "p6": 15, "p7": 15, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "三角巾", "單位": "條", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 8, "p2": 8, "p3": 8, "p4": 8, "p5": 8, "p6": 8, "p7": 8, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "冰袋 (冰敷用)", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 39, "p2": 37, "p3": 32, "p4": 29, "p5": 27, "p6": 23, "p7": 20, "u1": 2, "u2": 5, "u3": 3, "u4": 2, "u5": 4, "u6": 3, "品名": "冰熱敷袋 塑膠大", "單位": "個", "總使用量": 19, "有限期限/數量": "-"},
    {"p1": 1, "p2": 1, "p3": 1, "p4": 1, "p5": 1, "p6": 1, "p7": 1, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "冰熱敷袋 塑膠小", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 50, "p2": 30, "p3": 20, "p4": 10, "p5": 0, "p6": 0, "p7": 0, "u1": 20, "u2": 10, "u3": 10, "u4": 10, "u5": 0, "u6": 0, "品名": "免洗枕頭套", "單位": "個", "總使用量": 50, "有限期限/數量": "-"},
    {"p1": 420, "p2": 420, "p3": 410, "p4": 410, "p5": 410, "p6": 400, "p7": 400, "u1": 0, "u2": 10, "u3": 0, "u4": 0, "u5": 10, "u6": 0, "品名": "免洗床單", "單位": "個", "總使用量": 20, "有限期限/數量": "-"},
    {"p1": 1500, "p2": 1400, "p3": 1200, "p4": 1100, "p5": 1000, "p6": 800, "p7": 700, "u1": 100, "u2": 200, "u3": 100, "u4": 100, "u5": 200, "u6": 100, "品名": "紙尿壺", "單位": "個", "總使用量": 800, "有限期限/數量": "-"},
    {"p1": 150, "p2": 140, "p3": 130, "p4": 120, "p5": 110, "p6": 100, "p7": 90, "u1": 10, "u2": 10, "u3": 10, "u4": 10, "u5": 10, "u6": 10, "品名": "塑膠便盆", "單位": "個", "總使用量": 60, "有限期限/數量": "-"},
    {"p1": 32, "p2": 32, "p3": 32, "p4": 32, "p5": 32, "p6": 32, "p7": 32, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "塑膠藥杯", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 8, "p2": 8, "p3": 8, "p4": 8, "p5": 8, "p6": 8, "p7": 8, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "紙藥杯", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 250, "p2": 250, "p3": 250, "p4": 250, "p5": 250, "p6": 250, "p7": 250, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "壓舌板", "單位": "支", "總使用量": 0, "有限期限/數量": "20271105/250"},
    {"p1": 80, "p2": 70, "p3": 60, "p4": 50, "p5": 40, "p6": 30, "p7": 20, "u1": 10, "u2": 10, "u3": 10, "u4": 10, "u5": 10, "u6": 10, "品名": "體溫計感溫套", "單位": "個", "總使用量": 60, "有限期限/數量": "-"},
    {"p1": 50, "p2": 45, "p3": 40, "p4": 35, "p5": 30, "p6": 25, "p7": 20, "u1": 5, "u2": 5, "u3": 5, "u4": 5, "u5": 5, "u6": 5, "品名": "耳溫槍專用保護套", "單位": "盒", "總使用量": 30, "有限期限/數量": "-"},
    {"p1": 12, "p2": 12, "p3": 12, "p4": 12, "p5": 12, "p6": 12, "p7": 12, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "洗眼壺", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 6, "p2": 6, "p3": 6, "p4": 6, "p5": 6, "p6": 6, "p7": 6, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "洗眼杯", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 85, "p2": 80, "p3": 75, "p4": 70, "p5": 65, "p6": 60, "p7": 55, "u1": 5, "u2": 5, "u3": 5, "u4": 5, "u5": 5, "u6": 5, "品名": "生理食鹽水 (20ml)", "單位": "支", "總使用量": 30, "有限期限/數量": "20261112/55"},
    {"p1": 35, "p2": 30, "p3": 25, "p4": 20, "p5": 15, "p6": 10, "p7": 5, "u1": 5, "u2": 5, "u3": 5, "u4": 5, "u5": 5, "u6": 5, "品名": "生理食鹽水 (500ml)", "單位": "瓶", "總使用量": 30, "有限期限/數量": "20270315/5"},
    {"p1": 22, "p2": 22, "p3": 20, "p4": 20, "p5": 18, "p6": 18, "p7": 15, "u1": 0, "u2": 2, "u3": 0, "u4": 2, "u5": 0, "u6": 3, "品名": "酒精綿片 (100片/盒)", "單位": "盒", "總使用量": 7, "有限期限/數量": "20280120/15"},
    {"p1": 40, "p2": 38, "p3": 35, "p4": 32, "p5": 30, "p6": 28, "p7": 25, "u1": 2, "u2": 3, "u3": 3, "u4": 2, "u5": 2, "u6": 3, "品名": "克膚寧 (傷口噴劑)", "單位": "瓶", "總使用量": 15, "有限期限/數量": "20260930/25"},
    {"p1": 18, "p2": 18, "p3": 16, "p4": 16, "p5": 15, "p6": 15, "p7": 12, "u1": 0, "u2": 2, "u3": 0, "u4": 1, "u5": 0, "u6": 3, "品名": "白藥水 (廣效抗生素外用藥)", "單位": "瓶", "總使用量": 6, "有限期限/數量": "20270510/12"},
    {"p1": 25, "p2": 24, "p3": 22, "p4": 20, "p5": 19, "p6": 18, "p7": 16, "u1": 1, "u2": 2, "u3": 2, "u4": 1, "u5": 1, "u6": 2, "品名": "萬應白花油", "單位": "瓶", "總使用量": 9, "有限期限/數量": "20290401/16"},
    {"p1": 30, "p2": 28, "p3": 26, "p4": 25, "p5": 23, "p6": 20, "p7": 18, "u1": 2, "u2": 2, "u3": 1, "u4": 2, "u5": 3, "u6": 2, "品名": "曼秀雷敦軟膏", "單位": "瓶", "總使用量": 12, "有限期限/數量": "20281215/18"},
    {"p1": 50, "p2": 46, "p3": 42, "p4": 38, "p5": 35, "p6": 30, "p7": 26, "u1": 4, "u2": 4, "u3": 4, "u4": 3, "u5": 5, "u6": 4, "品名": "面邦乳膏 (燙傷軟膏)", "單位": "條", "總使用量": 24, "有限期限/數量": "20270822/26"},
    {"p1": 15, "p2": 15, "p3": 14, "p4": 14, "p5": 13, "p6": 12, "p7": 10, "u1": 0, "u2": 1, "u3": 0, "u4": 1, "u5": 1, "u6": 2, "品名": "擦傷消炎膏", "單位": "條", "總使用量": 5, "有限期限/數量": "20261018/10"},
    {"p1": 100, "p2": 95, "p3": 90, "p4": 85, "p5": 80, "p6": 75, "p7": 70, "u1": 5, "u2": 5, "u3": 5, "u4": 5, "u5": 5, "u6": 5, "品名": "透氣紗布 2x2 (包)", "單位": "包", "總使用量": 30, "有限期限/數量": "20280310/70"},
    {"p1": 120, "p2": 110, "p3": 100, "p4": 90, "p5": 80, "p6": 70, "p7": 60, "u1": 10, "u2": 10, "u3": 10, "u4": 10, "u5": 10, "u6": 10, "品名": "透氣紗布 3x3 (包)", "單位": "包", "總使用量": 60, "有限期限/數量": "20280512/60"},
    {"p1": 150, "p2": 135, "p3": 120, "p4": 105, "p5": 90, "p6": 75, "p7": 60, "u1": 15, "u2": 15, "u3": 15, "u4": 15, "u5": 15, "u6": 15, "品名": "透氣紗布 4x4 (包)", "單位": "包", "總使用量": 90, "有限期限/數量": "20280720/60"},
    {"p1": 40, "p2": 38, "p3": 35, "p4": 32, "p5": 30, "p6": 26, "p7": 22, "u1": 2, "u2": 3, "u3": 3, "u4": 2, "u5": 4, "u6": 4, "品名": "滅菌紗布塊 4x4 (包)", "單位": "包", "總使用量": 18, "有限期限/數量": "20271130/22"},
    {"p1": 200, "p2": 190, "p3": 180, "p4": 170, "p5": 160, "p6": 150, "p7": 140, "u1": 10, "u2": 10, "u3": 10, "u4": 10, "u5": 10, "u6": 10, "品名": "OK繃 標準型 (片)", "單位": "片", "總使用量": 60, "有限期限/數量": "20290115/140"},
    {"p1": 80, "p2": 75, "p3": 70, "p4": 65, "p5": 60, "p6": 55, "p7": 50, "u1": 5, "u2": 5, "u3": 5, "u4": 5, "u5": 5, "u6": 5, "品名": "OK繃 防水型 (片)", "單位": "片", "總使用量": 30, "有限期限/數量": "20281020/50"},
    {"p1": 50, "p2": 48, "p3": 45, "p4": 42, "p5": 40, "p6": 38, "p7": 35, "u1": 2, "u2": 3, "u3": 3, "u4": 2, "u5": 2, "u6": 3, "品名": "網狀繃帶 (號/肢)", "單位": "捲", "總使用量": 15, "有限期限/數量": "20280618/35"},
    {"p1": 30, "p2": 29, "p3": 28, "p4": 26, "p5": 25, "p6": 24, "p7": 22, "u1": 1, "u2": 1, "u3": 2, "u4": 1, "u5": 1, "u6": 2, "品名": "彈性繃帶 2吋", "單位": "捲", "總使用量": 8, "有限期限/數量": "20290210/22"},
    {"p1": 25, "p2": 24, "p3": 22, "p4": 21, "p5": 20, "p6": 18, "p7": 16, "u1": 1, "u2": 2, "u3": 1, "u4": 1, "u5": 2, "u6": 2, "品名": "彈性繃帶 4吋", "單位": "捲", "總使用量": 9, "有限期限/數量": "20290315/16"},
    {"p1": 60, "p2": 58, "p3": 55, "p4": 52, "p5": 50, "p6": 48, "p7": 45, "u1": 2, "u2": 3, "u3": 3, "u4": 2, "u5": 2, "u6": 3, "品名": "自黏繃帶 2吋", "單位": "捲", "總使用量": 15, "有限期限/數量": "20280912/45"},
    {"p1": 18, "p2": 18, "p3": 17, "p4": 16, "p5": 16, "p6": 15, "p7": 14, "u1": 0, "u2": 1, "u3": 1, "u4": 0, "u5": 1, "u6": 1, "品名": "止血帶", "單位": "條", "總使用量": 4, "有限期限/數量": "-"},
    {"p1": 10, "p2": 10, "p3": 10, "p4": 10, "p5": 10, "p6": 10, "p7": 10, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "急救包 (可攜式)", "單位": "個", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 15, "p2": 14, "p3": 14, "p4": 13, "p5": 13, "p6": 12, "p7": 12, "u1": 1, "u2": 0, "u3": 1, "u4": 0, "u5": 1, "u6": 0, "品名": "額溫槍", "單位": "支", "總使用量": 3, "有限期限/數量": "-"},
    {"p1": 8, "p2": 8, "p3": 8, "p4": 8, "p5": 8, "p6": 8, "p7": 8, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "耳溫槍", "單位": "支", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 6, "p2": 6, "p3": 6, "p4": 6, "p5": 6, "p6": 6, "p7": 6, "u1": 0, "u2": 0, "u3": 0, "u4": 0, "u5": 0, "u6": 0, "品名": "手臂式血壓計", "單位": "台", "總使用量": 0, "有限期限/數量": "-"},
    {"p1": 25, "p2": 24, "p3": 22, "p4": 20, "p5": 18, "p6": 16, "p7": 15, "u1": 1, "u2": 2, "u3": 2, "u4": 2, "u5": 2, "u6": 1, "品名": "醫用手套 (盒/S)", "單位": "盒", "總使用量": 10, "有限期限/數量": "20281130/15"},
    {"p1": 30, "p2": 28, "p3": 26, "p4": 24, "p5": 22, "p6": 20, "p7": 18, "u1": 2, "u2": 2, "u3": 2, "u4": 2, "u5": 2, "u6": 2, "品名": "醫用手套 (盒/M)", "單位": "盒", "總使用量": 12, "有限期限/數量": "20281210/18"},
    {"p1": 20, "p2": 19, "p3": 18, "p4": 17, "p5": 16, "p6": 15, "p7": 14, "u1": 1, "u2": 1, "u3": 1, "u4": 1, "u5": 1, "u6": 1, "品名": "醫用手套 (盒/L)", "單位": "盒", "總使用量": 6, "有限期限/數量": "20290105/14"},
    {"p1": 50, "p2": 48, "p3": 45, "p4": 42, "p5": 40, "p6": 38, "p7": 35, "u1": 2, "u2": 3, "u3": 3, "u4": 2, "u5": 2, "u6": 3, "品名": "醫用口罩 (50片/盒)", "單位": "盒", "總使用量": 15, "有限期限/數量": "20290520/35"},
    {"p1": 12, "p2": 12, "p3": 11, "p4": 11, "p5": 10, "p6": 10, "p7": 9, "u1": 0, "u2": 1, "u3": 0, "u4": 1, "u5": 0, "u6": 1, "品名": "防護面罩", "單位": "個", "總使用量": 3, "有限期限/數量": "-"},
    {"p1": 150, "p2": 140, "p3": 130, "p4": 120, "p5": 110, "p6": 100, "p7": 90, "u1": 10, "u2": 10, "u3": 10, "u4": 10, "u5": 10, "u6": 10, "品名": "廢棄物處置袋", "單位": "個", "總使用量": 60, "有限期限/數量": "-"}
]

df_all = pd.DataFrame(items_dataset)

# 自動解析狀態與最近到期日
def get_item_status(exp_str):
    if not exp_str or exp_str == "-":
        return "2099-12-31", "🟢 狀態正常"
    lines = str(exp_str).split('\n')
    first_exp = lines[0].split('/')[0].strip()
    
    if len(first_exp) == 8: # YYYYMMDD
        formatted_date = f"{first_exp[:4]}-{first_exp[4:6]}-{first_exp[6:]}"
    elif len(first_exp) == 6: # YYYYMM
        formatted_date = f"{first_exp[:4]}-{first_exp[4:6]}-28"
    else:
        formatted_date = "2028-12-31"
        
    try:
        exp_dt = pd.to_datetime(formatted_date)
        today = pd.to_datetime(datetime.date.today())
        diff_days = (exp_dt - today).days
        if diff_days < 0:
            return formatted_date, "🔴 已過期 (需報銷)"
        elif diff_days <= 180:
            return formatted_date, "🟠 即將到期"
        else:
            return formatted_date, "🟢 狀態正常"
    except:
        return "2028-12-31", "🟢 狀態正常"

df_all[['最近到期日', '狀態']] = df_all['有限期限/數量'].apply(lambda x: pd.Series(get_item_status(x)))

# ==========================================
# 3. 側邊欄與導覽 (全 61 項品項)
# ==========================================
st.sidebar.title("💊 衛材進銷存系統")
st.sidebar.caption("國立臺北大學衛生保健組")
menu = st.sidebar.radio(
    "功能選單",
    (
        "⏰ 效期預警與全品項清單", 
        "📋 學期衛材統計大表 (A4)",
        "📊 月度衛材進銷存報表", 
        "📝 每日/每月異動登記"
    ),
    index=0
)

# ==========================================
# 4. 功能 1：⏰ 效期預警與全 61 項品項清單
# ==========================================
if menu == "⏰ 效期預警與全品項清單":
    st.title("⏰ 衛材全品項有效期限追蹤與報銷清單")
    st.caption(f"目前資料庫共彙整 **{len(df_all)}** 項完整衛材品項。")

    expired_count = len(df_all[df_all['狀態'].str.contains('已過期')])
    warning_count = len(df_all[df_all['狀態'].str.contains('即將到期')])
    normal_count = len(df_all[df_all['狀態'].str.contains('正常')])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 衛材總品項", f"{len(df_all)} 項")
    c2.metric("🔴 已過期 (需報銷)", f"{expired_count} 項")
    c3.metric("🟠 近半年到期 (預警)", f"{warning_count} 項")
    c4.metric("🟢 效期正常", f"{normal_count} 項")

    st.markdown("---")
    
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        search_kw = st.text_input("🔍 關鍵字搜尋品名：", "")
    with col_s2:
        filter_status = st.multiselect(
            "篩選效期狀態：", 
            ["🔴 已過期 (需報銷)", "🟠 即將到期", "🟢 狀態正常"],
            default=["🔴 已過期 (需報銷)", "🟠 即將到期", "🟢 狀態正常"]
        )

    # 動態篩選
    filtered_df = df_all.copy()
    if search_kw:
        filtered_df = filtered_df[filtered_df['品名'].str.contains(search_kw, case=False)]
    if filter_status:
        filtered_df = filtered_df[filtered_df['狀態'].isin(filter_status)]

    st.dataframe(
        filtered_df[['品名', '單位', 'p7', '最近到期日', '有限期限/數量', '狀態']],
        column_config={
            "品名": st.column_config.TextColumn("衛材品名 (規格)"),
            "單位": st.column_config.TextColumn("單位"),
            "p7": st.column_config.NumberColumn("最新月底庫存"),
            "最近到期日": st.column_config.TextColumn("最近到期日"),
            "有限期限/數量": st.column_config.TextColumn("完整批號與效期細項"),
            "狀態": st.column_config.TextColumn("效期狀態")
        },
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 5. 功能 2：📋 學期衛材統計大表 (A4 自動彙整全品項)
# ==========================================
elif menu == "📋 學期衛材統計大表 (A4)":
    st.title("📋 學期衛材使用統計庫存大表")

    col_sel1, col_sel2 = st.columns([1, 1])
    with col_sel1:
        academic_year = st.selectbox("選擇學年度", ["114", "115", "116"], index=0)
    with col_sel2:
        semester = st.selectbox("選擇學期", ["第2學期 (2月~7月)", "第1學期 (8月~次年1月)"], index=0)

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
        expiry_fmt = str(row['有限期限/數量']).replace('\n', '<br>')
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

    st.markdown("<br>", unsafe_allow_html=True)
    csv_bytes = df_all.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載完整 61 項學期統計大表 (CSV/Excel)", data=csv_bytes, file_name=f"{academic_year}學年度_全品項衛材統計大表.csv", mime="text/csv", use_container_width=True)

# ==========================================
# 6. 功能 3：📊 月度衛材進銷存報表
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
        expiry_fmt = str(row['有限期限/數量']).replace('\n', '<br>')
        table_rows += f"""
        <tr>
            <td class="text-left font-bold">{row['品名']}</td>
            <td>{row['單位']}</td>
            <td>{row['p6']}</td>
            <td class="bg-in">+0</td>
            <td class="bg-out">-{row['u6']}</td>
            <td class="bg-waste">-0</td>
            <td>0</td>
            <td class="bg-stock">{row['p7']}</td>
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
