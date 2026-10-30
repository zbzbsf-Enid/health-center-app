# ==========================================
# 動態計算學年度、統計區間與表頭月份
# ==========================================
ay_int = int(academic_year)  # 例如 "114" 或 "115"

if "第2學期" in semester:
    # 第2學期：115年2月 ~ 115年7月 (年份 = 學年度 + 1)
    start_year = ay_int + 1
    end_year = ay_int + 1
    subtitle_date = f"{start_year}年2月 ～ {end_year}年7月"
    
    # 產出 13 個表頭欄位名稱
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
    
    # 產出 13 個表頭欄位名稱
    m_headers = [
        f"{start_year}/8<br>盤點", f"{start_year}/9<br>盤點", f"{start_year}/8<br>使用",
        f"{start_year}/10<br>盤點", f"{start_year}/9<br>使用", f"{start_year}/11<br>盤點",
        f"{start_year}/10<br>使用", f"{start_year}/12<br>盤點", f"{start_year}/11<br>使用",
        f"{end_year}/1<br>盤點", f"{start_year}/12<br>使用", f"{end_year}/2<br>盤點",
        f"{end_year}/1<br>使用"
    ]
