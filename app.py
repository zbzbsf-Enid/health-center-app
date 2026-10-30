# ==========================================
# 5. 功能 2：⏰ 衛材效期預警與 SMTP 自動真實寄信
# ==========================================
elif menu == "⏰ 衛材效期預警與 Email 提醒":
    st.title("⏰ 快過期衛材自動預警與真實郵件發送")
    st.caption("系統自動掃描全校衛材，點擊下方「真實寄出 Email」按鈕，系統會在背景直接發送通知信件！")

    expired_df = df_all[df_all['效期狀態'].str.contains('已過期')]
    warning_df = df_all[df_all['效期狀態'].str.contains('即將到期')]

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 衛材總品項", f"{len(df_all)} 項")
    c2.metric("🔴 已過期 (需急報銷)", f"{len(expired_df)} 項")
    c3.metric("🟠 近半年到期 (預警)", f"{len(warning_df)} 項")

    st.markdown("---")
    
    st.subheader("🚨 需關注/處理之衛材清單")
    alert_df = pd.concat([expired_df, warning_df])
    
    if len(alert_df) > 0:
        st.dataframe(
            alert_df[['品名', '單位', 'p7', '效期狀態', '有限期限/數量']],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### ✉️ 設定發送參數並真實寄出")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sender_email = st.text_input("系統發件者 Gmail：", value="zbzbsf@gm.ntpu.edu.tw")
            sender_password = st.text_input("Google 16 位數應用程式密碼：", type="password", help="請至 Google 帳戶安全性建立應用程式密碼")
        with col_m2:
            recipient_email = st.text_input("接收通知之 Email：", value="health@mail.ntpu.edu.tw")
            email_subject = f"【衛保組效期提醒】衛材快過期/已過期清單通知 ({datetime.date.today().strftime('%Y-%m-%d')})"

        items_detail = ""
        for _, r in alert_df.iterrows():
            items_detail += f"• {r['品名']} (剩餘: {r['p7']} {r['單位']}) - 狀態: {r['效期狀態']} [批號效期: {r['有限期限/數量']}]\n"
            
        email_body = f"""衛保組同仁/主管 您好：

以下為今日系統自動掃描之【快過期/已過期衛材清單】，請協助留意並進行處置或報銷流程：

{items_detail}
發起時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
國立臺北大學衛生保健組 衛材管理系統
"""

        st.text_area("預覽即將發送之信件內文：", value=email_body, height=180)

        # 真實發送 Email 邏輯 (使用 Port 587 + TLS)
        if st.button("🚀 立即點擊：背景自動真實寄出 Email"):
            if "your_email" in sender_email or not sender_password:
                st.error("❌ 請先填寫正確的發件者 Gmail 以及 16 位數應用程式密碼！")
            else:
                try:
                    with st.spinner("信件寄送中，請稍候..."):
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = recipient_email
                        msg['Subject'] = email_subject
                        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))

                        # 使用 587 埠號與 TLS 加密，解決連線意外中斷問題
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.ehlo()
                        server.starttls()
                        server.login(sender_email, sender_password.replace(" ", ""))
                        server.sendmail(sender_email, recipient_email.split(';'), msg.as_string())
                        server.quit()

                    st.success(f"🎉 郵件已成功寄出！收件人 ({recipient_email}) 馬上就會收到系統通知。")
                except Exception as e:
                    st.error(f"❌ 寄送失敗，錯誤原因：{str(e)}")

    else:
        st.success("🎉 目前所有衛材效期皆正常，無快過期或已過期之品項！")
