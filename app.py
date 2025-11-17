import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# OpenWeatherMap API Key (실제 키로 대체해야 함)
API_KEY = "42a1c1f7d750079299f8341d808ef0a1"

st.set_page_config(page_title="날씨 모니터링 프로토타입", page_icon="🌦️")
st.title("🌦️ 실시간 날씨 모니터링 대시보드 (프로토타입)")

# --- 1. 위젯 사용 (실습 예제 1, 2) ---
st.sidebar.header("도시 선택")
# 1. 텍스트 입력 위젯
city = st.sidebar.text_input("도시 이름을 영어로 입력하세요", "Seoul")

# 2. 버튼 위젯
if st.sidebar.button("날씨 정보 가져오기"):
    if not API_KEY.startswith("여기에"):
        # API 호출
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
        
        try:
            response = requests.get(url)
            response.raise_for_status() # 오류 발생 시 예외 처리
            data = response.json()

            # --- 2. 데이터 표시 (실습 예제 2) ---
            st.subheader(f"🏙️ {data['name']}의 현재 날씨")
            
            # 3. 컬럼 및 메트릭 위젯 (도전 과제: 기초 통계)
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 기온", f"{data['main']['temp']} °C")
            col2.metric("💧 습도", f"{data['main']['humidity']} %")
            col3.metric("💨 풍속", f"{data['wind']['speed']} m/s")
            
            st.metric("날씨", f"{data['weather'][0]['description']} {data['weather'][0]['icon']}", 
                      delta=f"체감: {data['main']['feels_like']} °C")

            # --- 3. 데이터 시각화 (도전 과제: 차트) ---
            # (1일차) 우선 API 응답 원본(JSON)을 확인합니다.
            st.subheader("📊 API 응답 원본 (Raw JSON)")
            st.json(data)
            
            # 세션 상태에 데이터 저장 (다음 단계를 위해)
            st.session_state['weather_data'] = data

        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                st.error("API 키가 유효하지 않습니다. OpenWeatherMap에서 발급받은 키를 확인하세요.")
            elif response.status_code == 404:
                st.error(f"'{city}' 도시를 찾을 수 없습니다. 영문 이름을 확인하세요.")
            else:
                st.error(f"API 호출 중 오류 발생: {err}")
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")

    else:
        st.warning("OpenWeatherMap API 키를 입력해주세요.")
        st.info("https://openweathermap.org/appid 에서 무료 키를 발급받을 수 있습니다.")

else:
    st.info("👆 사이드바에서 도시 이름을 입력하고 버튼을 클릭하세요.")

# --- 4. CSV 업로드 대신 '샘플 데이터' 생성 (실습 예제 3 변형) ---
st.subheader("💾 (참고) 샘플 데이터프레임")
# (1일차) 지금은 API 응답을 직접 사용하므로, 
# '실습 예제 3'의 파일 업로드 기능은 '수집 데이터 표시'로 대체합니다.
if 'weather_data' in st.session_state:
    data = st.session_state['weather_data']
    sample_df = pd.DataFrame({
        "도시": [data['name']],
        "기온": [data['main']['temp']],
        "습도": [data['main']['humidity']],
        "날씨": [data['weather'][0]['description']],
        "수집 시간": [datetime.fromtimestamp(data['dt'])]
    })
    st.dataframe(sample_df)
else:
    st.write("아직 조회된 날씨 데이터가 없습니다.")