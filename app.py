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
        max-width: 1180px; /* A4 橫向最適寬度 */
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
        font-size: 11px; /* 欄位多，調小字級以符合 A4 寬度 */
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
# 3. 頁面控制選單
# ==========================================
st.title("📋 學期衛材統計庫存報表")

col_sel1, col_sel2 = st.columns([1, 1])
with col_sel1:
    academic_year = st.selectbox("選擇學年度", ["114", "115", "116"], index=0)
with col_sel2:
    semester = st.selectbox("選擇學期", ["第2學期 (2月~7月)", "第1學期 (8月~次年1月)"], index=0)

# ==========================================
# 4. 準備對應 Excel 學期統計表資料
# ==========================================
sample_semester_data = [
    {
        "品名": "3M 1吋膠帶 (12捲/盒)", "單位": "捲",
        "p1": 132, "p2": 128, "u1": 4, "p3": 120, "u2": 8, "p4": 120, "u3": 0, "p5": 120, "u4": 0, "p6": 120, "u5": 0, "p7": 108, "u6": 1,
        "總使用量": 13, "有效期限/數量": "202802/1\n202909/3\n203003/4"
    },
    {
        "品名": "3M 1吋膠帶 (含切台)", "單位": "捲",
        "p1": 26, "p2": 26, "u1": 0, "p3": 26, "u2": 0, "p4": 26, "u3": 0, "p5": 26, "u4": 0, "p6": 26, "u5": 0, "p7": 25, "u6": 1,
        "總使用量": 1, "有效期限/數量": "20251127/25"
    },
    {
        "品名": "3M彈繃3吋 (捲)", "單位": "捲",
        "p1": 55, "p2": 51, "u1": 4, "p3": 46, "u2": 5, "p4": 46, "u3": 0, "p5": 40, "u4": 6, "p6": 36, "u5": 4, "p7": 34, "u6": 2,
        "總使用量": 21, "有效期限/數量": "20260321/11\n20300609/23"
    },
    {
        "品名": "3吋棉棒 (10枝/包)", "單位": "包",
        "p1": 115, "p2": 110, "u1": 5, "p3": 110, "u2": 0, "p4": 110, "u3": 0, "p5": 110, "u4": 0, "p6": 110, "u5": 0, "p7": 110, "u6": 0,
        "總使用量": 5, "有效期限/數量": "20260815/85\n20281105/25"
    },
    {
        "品名": "沖洗棉棒 (5枝/包)", "單位": "包",
        "p1": 400, "p2": 300, "u1": 100, "p3": 250, "u2": 50, "p4": 250, "u3": 0, "p5": 250, "u4": 0, "p6": 225, "u5": 25, "p7": 200, "u6": 25,
        "總使用量": 200, "有效期限/數量": "20270911/100\n20280602/50"
    }
]
df_semester = pd.DataFrame(sample_semester_data)

# 動態判斷標題月份
if "第2學期" in semester:
    m_headers = ["114/2<br>盤點", "115/3<br>盤點", "115/2<br>使用", "115/4<br>盤點", "115/3<br>使用", "115/5<br>盤點", "115/4<br>使用", "115/6<br>盤點", "115/5<br>使用", "115/7<br>盤點", "115/6<br>使用", "115/8<br>盤點", "115/7<br>使用"]
    subtitle_date = "115年2月 ～ 115年7月"
else:
    m_headers = ["114/8<br>盤點", "114/9<br>盤點", "114/8<br>使用", "114/10<br>盤點", "114/9<br>使用", "114/11<br>盤點", "114/10<br>使用", "114/12<br>盤點", "114/11<br>使用", "115/1<br>盤點", "114/12<br>使用", "115/2<br>盤點", "115/1<br>使用"]
    subtitle_date = "114年8月 ～ 115年1月"

# ==========================================
# 5. 生成 HTML 表格
# ==========================================
table_rows = ""
for _, row in df_semester.iterrows():
    expiry_fmt = str(row['有效期限/數量']).replace('\n', '<br>')
    table_rows += f"""
    <tr>
        <td class="text-left font-bold">{row['品名']}</td>
        <td>{row['單位']}</td>
        <td>{row['p1']}</td>
        <td>{row['p2']}</td>
        <td>{row['u1']}</td>
        <td>{row['p3']}</td>
        <td>{row['u2']}</td>
        <td>{row['p4']}</td>
        <td>{row['u3']}</td>
        <td>{row['p5']}</td>
        <td>{row['u4']}</td>
        <td>{row['p6']}</td>
        <td>{row['u5']}</td>
        <td>{row['p7']}</td>
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
                <th>{m_headers[0]}</th>
                <th>{m_headers[1]}</th>
                <th>{m_headers[2]}</th>
                <th>{m_headers[3]}</th>
                <th>{m_headers[4]}</th>
                <th>{m_headers[5]}</th>
                <th>{m_headers[6]}</th>
                <th>{m_headers[7]}</th>
                <th>{m_headers[8]}</th>
                <th>{m_headers[9]}</th>
                <th>{m_headers[10]}</th>
                <th>{m_headers[11]}</th>
                <th>{m_headers[12]}</th>
                <th style="background-color: #c8e6c9;">總使用量</th>
                <th style="width: 14%;">有效期限/數量</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
</div>
"""

# 使用 st.html() 正確渲染
st.html(full_html)

# ==========================================
# 6. 下載與列印區
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_d1, col_d2 = st.columns([1, 1])

with col_d1:
    csv_bytes = df_semester.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下載學期統計大表 (CSV/Excel)",
        data=csv_bytes,
        file_name=f"{academic_year}學年度_{semester[:4]}_衛材統計大表.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_d2:
    st.info("💡 **A4 橫向列印**：按下 `Ctrl + P` (Mac 為 `Cmd + P`)，目標列印區選擇「另存為 PDF」，方向選擇 **「橫向」** 即可。")
