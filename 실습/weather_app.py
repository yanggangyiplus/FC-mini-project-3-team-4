import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="🌤 실시간 서울 날씨 대시보드", page_icon="🌤")

API_KEY = 'c1a16b0f5bad3ca2688a448198987635'  # 🔑 여기에 본인 키 입력
CITY_ID = 1835847
URL = f"https://api.openweathermap.org/data/2.5/weather?id={CITY_ID}&appid={API_KEY}&units=metric&lang=kr"

st.title("🌤 실시간 서울 날씨 모니터링")
st.caption("데이터 출처: OpenWeatherMap API")

# 데이터 수집
response = requests.get(URL)
data = response.json()

# 확인용 출력
st.write(data)

# 데이터 파싱
temp = data['main']['temp']
feels_like = data['main']['feels_like']
humidity = data['main']['humidity']
pressure = data['main']['pressure']
weather = data['weather'][0]['description']
wind = data['wind']['speed']
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 메트릭 표시
col1, col2, col3 = st.columns(3)
col1.metric("🌡 현재 온도 (°C)", f"{temp:.1f}", delta=None)
col2.metric("💧 습도 (%)", f"{humidity}%")
col3.metric("💨 풍속 (m/s)", f"{wind}")

st.info(f"현재 상태: **{weather}**, 체감온도 {feels_like}°C (기압: {pressure}hPa)")

# 시각화를 위한 데이터 프레임 생성 (테스트용)
df = pd.DataFrame({
    "항목": ["기온", "체감온도", "습도", "풍속"],
    "값": [temp, feels_like, humidity, wind]
})

fig = px.bar(df, x="항목", y="값", color="항목", title="현재 날씨 지표 비교")
st.plotly_chart(fig, use_container_width=True)

# 새로고침 버튼
if st.button("🔄 새로고침"):
    st.experimental_rerun()

st.caption(f"마지막 업데이트: {timestamp}")

# 60초(60000ms)마다 새로고침
st_autorefresh(interval=60000, key="datarefresh")
