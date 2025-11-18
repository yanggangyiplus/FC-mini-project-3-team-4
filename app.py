import streamlit as st

# ⚠️ 중요: set_page_config는 항상 맨 위에!
st.set_page_config(page_title="날씨 모니터링 대시보드", page_icon="🌦️")

import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 로컬 테스트용: secrets 없이 실행
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (KeyError, FileNotFoundError):
    API_KEY = "test_local_key"

st.title("🌦️ 실시간 날씨 모니터링 대시보드")

# --- 데이터 저장을 위한 초기화 ---
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- 1. 위젯 사용 ---
st.sidebar.header("도시 선택")
city = st.sidebar.text_input("도시 이름을 영어로 입력하세요", "Seoul")

if st.sidebar.button("날씨 정보 가져오기"):
    if API_KEY != "test_local_key":
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            st.subheader(f"🏙️ {data['name']}의 현재 날씨")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 기온", f"{data['main']['temp']} °C", f"{data['main']['feels_like']} °C 체감")
            col2.metric("💧 습도", f"{data['main']['humidity']} %")
            col3.metric("💨 풍속", f"{data['wind']['speed']} m/s")
            
            current_data = {
                "도시": data['name'],
                "기온": data['main']['temp'],
                "습도": data['main']['humidity'],
                "풍속": data['wind']['speed'],
                "날씨": data['weather'][0]['description'],
                "수집 시간": datetime.fromtimestamp(data['dt'])
            }
            
            st.session_state['history'].append(current_data)
            
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                st.error("API 키가 유효하지 않습니다.")
            elif response.status_code == 404:
                st.error(f"'{city}' 도시를 찾을 수 없습니다.")
            else:
                st.error(f"API 호출 중 오류 발생: {err}")
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
    else:
        st.info("🧪 로컬 테스트 모드: 샘플 데이터를 생성합니다.")
        # 테스트용 더미 데이터
        import random
        current_data = {
            "도시": city,
            "기온": round(random.uniform(15, 30), 1),
            "습도": random.randint(40, 80),
            "풍속": round(random.uniform(1, 10), 1),
            "날씨": random.choice(["맑음", "흐림", "비"]),
            "수집 시간": datetime.now()
        }
        st.session_state['history'].append(current_data)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ 기온", f"{current_data['기온']} °C")
        col2.metric("💧 습도", f"{current_data['습도']} %")
        col3.metric("💨 풍속", f"{current_data['풍속']} m/s")
        st.success("✅ 샘플 데이터가 추가되었습니다!")

# --- 누적 데이터 시각화 ---
if st.session_state['history']:
    st.subheader("📊 데이터 수집 기록")
    
    df = pd.DataFrame(st.session_state['history'])
    st.dataframe(df)
    
    st.subheader("📈 시간에 따른 기온 및 습도 변화")
    fig = px.line(df, x='수집 시간', y=['기온', '습도'],
                  title=f"{city} 날씨 변화", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📈 기초 통계량")
    st.dataframe(df[['기온', '습도', '풍속']].describe())
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 수집된 데이터를 CSV로 다운로드",
        data=csv,
        file_name=f'{city}_weather_history.csv',
        mime='text/csv'
    )
else:
    st.info("👆 사이드바에서 도시 날씨를 조회하면 기록이 시작됩니다.")