import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# (배포용) Streamlit 클라우드의 Secrets에서 API 키 가져오기
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except KeyError:
    st.error("API 키가 설정되지 않았습니다. Streamlit Cloud의 Secrets에 등록해주세요.")
    # 로컬 테스트용 임시 키 (배포 시 이 부분은 무시됨)
    API_KEY = "local_test_key" # 실제 배포 시 이 키로는 작동하지 않습니다.

st.set_page_config(page_title="날씨 모니터링 대시보드", page_icon="🌦️")
st.title("🌦️ 실시간 날씨 모니터링 대시보드")

# --- 데이터 저장을 위한 초기화 ---
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- 1. 사이드바: 도시 입력 및 API 호출 ---
st.sidebar.header("도시 선택")
city = st.sidebar.text_input("도시 이름을 영어로 입력하세요", "Seoul")

if st.sidebar.button("날씨 정보 가져오기"):
    # API 키가 "local_test_key" 이거나 "여기에..." 같은 플레이스홀더가 아닌지 확인
    if API_KEY and API_KEY != "local_test_key" and not API_KEY.startswith("여기에"):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
        try:
            response = requests.get(url)
            response.raise_for_status() # 오류가 났을 때 예외 발생
            data = response.json()

            # --- 2. 현재 날씨 표시 ---
            st.subheader(f"🏙️ {data['name']}의 현재 날씨")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 기온", f"{data['main']['temp']} °C", f"{data['main']['feels_like']} °C 체감")
            col2.metric("💧 습도", f"{data['main']['humidity']} %")
            col3.metric("💨 풍속", f"{data['wind']['speed']} m/s")

            # --- 3. 데이터 누적 ---
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
                st.error("API 키가 유효하지 않습니다. Streamlit Cloud Secrets를 확인해주세요.")
            elif response.status_code == 404:
                st.error(f"'{city}' 도시를 찾을 수 없습니다. 영문 도시명을 확인해주세요.")
            else:
                st.error(f"API 호출 중 오류 발생: {err}")
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
    else:
        if API_KEY == "local_test_key":
            st.warning("API 키가 Streamlit Secrets에 설정되지 않았습니다. 로컬에서는 API 호출이 제한됩니다.")
        else:
            st.warning("유효한 API 키를 입력해주세요.")

# --- [수정] 4. 누적 데이터 시각화 (요청사항 반영) ---
if st.session_state['history']:
    st.subheader("📊 전체 데이터 수집 기록")
    
    # 1. [요청 2] 전체 데이터를 데이터프레임으로 변환하여 항상 표시
    df = pd.DataFrame(st.session_state['history'])
    # 수집 시간을 기준으로 내림차순 정렬 (최신 데이터가 위로)
    df_sorted = df.sort_values(by="수집 시간", ascending=False)
    st.dataframe(df_sorted, use_container_width=True)

    # 2. [요청 5] 전체 데이터 CSV 다운로드 버튼
    # - 정렬된 데이터프레임(df_sorted)을 CSV로 변환
    csv = df_sorted.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 전체 데이터를 CSV로 다운로드",
        data=csv,
        file_name='all_weather_history.csv',
        mime='text/csv'
    )

    st.divider() # 시각 구분을 위한 구분선

    # 3. [요청 4] 도시별로 그래프 및 통계량 표시
    # - [요청 1, 3]의 원인이던 기존 로직 및 selectbox 제거
    
    # 데이터프레임에서 고유한 도시 목록을 가져옴
    all_cities = df['도시'].unique()
    
    for selected_city in all_cities:
        # 현재 순회 중인 도시의 데이터만 필터링
        city_df = df[df['도시'] == selected_city]
        
        # (1) 도시별 꺾은선 그래프
        st.subheader(f"📈 {selected_city}의 시간에 따른 기온 및 습도 변화")
        fig = px.line(city_df, x='수집 시간', y=['기온', '습도'],
                      title=f"{selected_city} 날씨 변화", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # (2) 도시별 기초 통계량
        st.subheader(f"📊 {selected_city}의 기초 통계량")
        st.dataframe(city_df[['기온', '습도', '풍속']].describe(), use_container_width=True)
        
        st.divider() # 도시별 섹션 구분

else:
    # 기록이 하나도 없을 때
    st.info("👆 사이드바에서 도시 날씨를 조회하면 기록이 시작됩니다.")

# --- 5. 사이드바 하단: 기록 초기화 ---
if st.sidebar.button("🗑️ 모든 기록 초기화"):
    st.session_state['history'] = []
    st.rerun()