import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. 頁面設定與 A4 清新風格 CSS 注入
# ==========================================
st.set_page_config(
    page_title="衛材使用統計表 - 北大衛保組",
    page_icon="📋",
    layout="wide"
)

# A4 橫向與清新現代風格樣式
st.markdown("""
<style>
    /* 清新風格色彩變數 */
    :root {
        --primary-color: #2e7d32;
        --header-bg: #e8f5e9;
        --header-text: #1b5e20;
        --alt-row-bg: #f9fbf9;
        --border-color: #c8e6c9;
    }

    /* A4 視圖容器 */
    .a4-container {
        background-color: #ffffff;
        width: 100%;
        max-width: 1100px; /* A4 橫向比例優化 */
        margin: 0 auto;
        padding: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }

    /* 報表主標題 */
    .report-header {
        text-align: center;
        color: #1b5e20;
        font-family: "PingFang TC", "Microsoft JhengHei", sans-serif;
        margin-bottom: 20px;
    }
    .report-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }
    .report-subtitle {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }

    /* 清新表格樣式 */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        color: #333;
        margin-top: 15px;
    }
    .custom-table th {
        background-color: var(--header-bg);
        color: var(--header-text);
        font-weight: 600;
        padding: 10px 6px;
        border: 1px solid var(--border-color);
        text-align: center;
        white-space: pre-line;
    }
    .custom-table td {
        padding: 8px 6px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .custom-table tr:nth-child(even) {
        background-color: var(--alt-row-bg);
    }
    .custom-table tr:hover {
        background-color: #f1f8e9;
    }
    .text-left { text-align: left !important; }
    .text-right { text-align: right !important; }
    .font-bold { font-weight: bold; }
    .highlight-cell { background-color: #e8f5e9; font-weight: bold; color: #2e7d32; }

    /* A4 列印優化與按鈕隱藏 */
    @media print {
        @page {
            size: A4 landscape;
            margin: 10mm;
        }
        section[data-testid="stSidebar"], 
        .stButton, 
        header, 
        footer {
            display: none !important;
        }
        .a4-container {
            box-shadow: none !important;
            border: none !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 標題與選單列
# ==========================================
st.title("📑 衛材統計庫存報表匯出")

col_sel1, col_sel2, col_btn = st.columns([2, 2, 2])
with col_sel1:
    academic_year = st.selectbox("選擇學年度", ["114", "115", "116"], index=0)
with col_sel2:
    semester = st.selectbox("選擇學期", ["第2學期 (2月~7月)", "第1學期 (8月~次年1月)"], index=0)

# ==========================================
# 3. 模擬/讀取 114-2 衛材統計資料 (對應您上傳的格式)
# ==========================================
# 實際環境中此部分會由 pd.read_csv / Google Sheets 自動整合產出
sample_data = [
    {"品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲", "114/2盤點": 132, "115/3盤點": 128, "115/2使用": 4, "115/4盤點": 120, "115/3使用": 8, "115/5盤點": 120, "115/4使用": 0, "115/6盤點": 120, "115/5使用": 0, "115/7盤點": 120, "115/6使用": 0, "115/8盤點": 108, "115/7使用": 1, "總使用量": 13, "有效期限/數量": "202802/1\n202909/3\n203003/4"},
    {"品名": "3M 1吋膠帶 (含切台)", "單位": "捲", "114/2盤點": 26, "115/3盤點": 26, "115/2使用": 0, "115/4盤點": 26, "115/3使用": 0, "115/5盤點": 26, "115/4使用": 0, "115/6盤點": 26, "115/5使用": 0, "115/7盤點": 26, "115/6使用": 0, "115/8盤點": 25, "115/7使用": 1, "總使用量": 1, "有效期限/數量": "20251127/25"},
    {"品名": "3M彈繃3吋 (捲)", "單位": "捲", "114/2盤點": 55, "115/3盤點": 51, "115/2使用": 4, "115/4盤點": 46, "115/3使用": 5, "115/5盤點": 46, "115/4使用": 0, "115/6盤點": 40, "115/5使用": 6, "115/7盤點": 36, "115/6使用": 4, "115/8盤點": 34, "115/7使用": 2, "總使用量": 21, "有效期限/數量": "20260321/11\n20300609/23"},
    {"品名": "3吋棉棒 (10枝/包)", "單位": "包", "114/2盤點": 115, "115/3盤點": 110, "115/2使用": 5, "115/4盤點": 110, "115/3使用": 0, "115/5盤點": 110, "115/4使用": 0, "115/6盤點": 110, "115/5使用": 0, "115/7盤點": 110, "115/6使用": 0, "115/8盤點": 110, "115/7使用": 0, "總使用量": 5, "有效期限/數量": "20260815/85\n20281105/25"},
    {"品名": "沖洗棉棒 (5枝/包)", "單位": "包", "114/2盤點": 400, "115/3盤點": 300, "115/2使用": 100, "115/4盤點": 250, "115/3使用": 50, "115/5盤點": 250, "115/4使用": 0, "115/6盤點": 250, "115/5使用": 0, "115/7盤點": 225, "115/6使用": 25, "115/8盤點": 200, "115/7使用": 25, "總使用量": 200, "有效期限/數量": "20270911/100\n20280602/50"},
]
df_report = pd.DataFrame(sample_data)

# ==========================================
# 4. 渲染 A4 報表 HTML
# ==========================================
st.markdown("---")

# 生成 HTML 表格列內容
table_rows_html = ""
for _, row in df_report.iterrows():
    # 處理有效期限換行顯示
    expiry_fmt = str(row['有效期限/數量']).replace('\n', '<br>')
    table_rows_html += f"""
    <tr>
        <td class="text-left font-bold">{row['品名']}</td>
        <td>{row['單位']}</td>
        <td>{row['114/2盤點']}</td>
        <td>{row['115/3盤點']}</td>
        <td>{row['115/2使用']}</td>
        <td>{row['115/4盤點']}</td>
        <td>{row['115/3使用']}</td>
        <td>{row['115/5盤點']}</td>
        <td>{row['115/4使用']}</td>
        <td>{row['115/6盤點']}</td>
        <td>{row['115/5使用']}</td>
        <td>{row['115/7盤點']}</td>
        <td>{row['115/6使用']}</td>
        <td>{row['115/8盤點']}</td>
        <td>{row['115/7使用']}</td>
        <td class="highlight-cell">{row['總使用量']}</td>
        <td class="text-left" style="font-size: 11px;">{expiry_fmt}</td>
    </tr>
    """

# 完整 A4 視圖渲染
a4_html = f"""
<div class="a4-container">
    <div class="report-header">
        <div class="report-title">{academic_year}學年度第2學期學期衛材使用統計表</div>
        <div class="report-subtitle">國立臺北大學衛生保健組 ｜ 統計區間：115年2月 ～ 115年7月</div>
    </div>
    
    <table class="custom-table">
        <thead>
            <tr>
                <th style="width: 15%;">品名</th>
                <th style="width: 4%;">單位</th>
                <th>114/2<br>盤點量</th>
                <th>115/3<br>盤點量</th>
                <th>115/2<br>使用量</th>
                <th>115/4<br>盤點量</th>
                <th>115/3<br>使用量</th>
                <th>115/5<br>盤點量</th>
                <th>115/4<br>使用量</th>
                <th>115/6<br>盤點量</th>
                <th>115/5<br>盤點量</th>
                <th>115/7<br>盤點量</th>
                <th>115/6<br>使用量</th>
                <th>115/8<br>盤點量</th>
                <th>115/7<br>使用量</th>
                <th style="background-color: #c8e6c9;">總使用量</th>
                <th style="width: 12%;">有效期限/數量</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
</div>
"""

st.markdown(a4_html, unsafe_allow_html=True)

# ==========================================
# 5. 下載與列印功能區
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_down1, col_down2 = st.columns([1, 1])

with col_down1:
    # 匯出 CSV 檔
    csv_data = df_report.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下載 Excel/CSV 格式報表",
        data=csv_data,
        file_name=f"{academic_year}學年度第2學期衛材使用統計表.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_down2:
    # 提示列印 A4 功能
    st.info("💡 **提示**：直接按下鍵盤 `Ctrl + P` (或 Mac `Cmd + P`) 即可直接列印或另存為 **A4 橫向 PDF 檔案**！")
