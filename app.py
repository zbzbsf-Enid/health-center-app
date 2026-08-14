import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="衛保組衛材管理系統", layout="wide", page_icon="🏥")

# 🔗 請將下方括號內的網址替換成您的 Google 試算表連結
URL = "https://docs.google.com/spreadsheets/d/12gjsQ8Zh3Ozf4_k9tFn_r2XMj4EEOFXwo2NppOhrZ90/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(sheet_name, expected_cols):
    try:
        df = conn.read(spreadsheet=URL, worksheet=sheet_name, ttl="0")
        if df is None or df.empty:
            return pd.DataFrame(columns=expected_cols)
        return df
    except Exception:
        return pd.DataFrame(columns=expected_cols)

def save_sheet(sheet_name, df):
    conn.update(spreadsheet=URL, worksheet=sheet_name, data=df)

# 載入資料
df_items = load_sheet("items", ["品名", "單位", "總庫存", "安全庫存"])
df_trans = load_sheet("transactions", ["日期", "品名", "異動類型", "數量", "備註"])
df_expiry = load_sheet("expiry", ["品名", "到期年月", "數量"])

# 選單與 UI 介面
st.sidebar.title("🏥 衛保組衛材管理")
menu = st.sidebar.radio("📌 功能選單", ["📊 庫存儀表板", "📥 入庫與領用", "📋 月盤點作業", "📈 統計與匯出"])

if menu == "📊 庫存儀表板":
    st.header("📊 庫存與預警儀表板")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚠️ 低庫存預警 (低於安全庫存)")
        if not df_items.empty:
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
        if not df_expiry.empty:
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

elif menu == "📥 入庫與領用":
    st.header("📥 日常入庫與領用登記")
    item_list = df_items['品名'].dropna().tolist() if not df_items.empty else []
    
    st.subheader("➕ 新增/異動衛材紀錄")
    with st.form("transaction_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            t_date = st.date_input("日期", datetime.now())
            t_item = st.selectbox("品名 (若無請選擇建立新品項)", item_list + ["新建品項..."]) if item_list else "新建品項..."
            if t_item == "新建品項...":
                new_item_name = st.text_input("輸入新品名")
                new_item_unit = st.text_input("單位 (如: 包, 盒, 個)", value="個")
                new_item_safe = st.number_input("安全庫存量", min_value=1, value=10)
        with col2:
            t_type = st.selectbox("異動類型", ["採購入庫", "領用 (出庫)"])
            t_qty = st.number_input("數量", min_value=1, step=1)
        with col3:
            t_note = st.text_input("備註 (領用事由或採購批號)")
        
        submit = st.form_submit_button("送出並儲存至雲端")
        
        if submit:
            target_name = new_item_name if (t_item == "新建品項..." or not item_list) else t_item
            
            # 若為新建品項，加入 items 表
            if t_item == "新建品項..." or not item_list:
                new_item_row = pd.DataFrame([{"品名": target_name, "單位": new_item_unit, "總庫存": t_qty if t_type == "採購入庫" else 0, "安全庫存": new_item_safe}])
                df_items = pd.concat([df_items, new_item_row], ignore_index=True)
            else:
                idx = df_items.index[df_items['品名'] == target_name].tolist()[0]
                curr = int(df_items.at[idx, '總庫存'])
                df_items.at[idx, '總庫存'] = curr + t_qty if t_type == "採購入庫" else curr - t_qty

            # 寫入異動紀錄
            new_trans = pd.DataFrame([{"日期": str(t_date), "品名": target_name, "異動類型": t_type, "數量": t_qty, "備註": t_note}])
            df_trans = pd.concat([df_trans, new_trans], ignore_index=True)
            
            save_sheet("items", df_items)
            save_sheet("transactions", df_trans)
            st.success(f"✅ 已更新雲端資料：{target_name} {t_type} {t_qty}")
            st.rerun()

elif menu == "📋 月盤點作業":
    st.header("📋 月度盤點與庫存校正")
    if not df_items.empty:
        item_to_check = st.selectbox("選擇盤點品項", df_items['品名'].dropna().tolist())
        current_stock = int(df_items[df_items['品名'] == item_to_check]['總庫存'].values[0])
        
        st.write(f"目前雲端帳面庫存： **{current_stock}**")
        actual_stock = st.number_input("請輸入實際盤點數量", min_value=0, value=current_stock, step=1)
        
        if st.button("確認盤點校正"):
            diff = actual_stock - current_stock
            if diff != 0:
                t_type = "盤盈" if diff > 0 else "盤虧"
                new_trans = pd.DataFrame([{"日期": str(datetime.now().date()), "品名": item_to_check, "異動類型": f"盤點校正-{t_type}", "數量": abs(diff), "備註": "月盤點"}])
                df_trans = pd.concat([df_trans, new_trans], ignore_index=True)
                
                idx = df_items.index[df_items['品名'] == item_to_check].tolist()[0]
                df_items.at[idx, '總庫存'] = actual_stock
                
                save_sheet("items", df_items)
                save_sheet("transactions", df_trans)
                st.success(f"✅ 已校正雲端庫存為 {actual_stock}")
                st.rerun()

elif menu == "📈 統計與匯出":
    st.header("📈 異動紀錄總覽")
    st.dataframe(df_trans, hide_index=True, use_container_width=True)
