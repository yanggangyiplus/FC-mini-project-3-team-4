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
    API_KEY = "local_test_key"

st.set_page_config(page_title="날씨 모니터링 대시보드", page_icon="🌦️")
st.title("🌦️ 실시간 날씨 모니터링 대시보드")

# --- [NEW] 실습 2/3 통합: 데이터 저장을 위한 초기화 ---
# session_state에 'history' 키가 없으면 빈 리스트로 초기화
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- 1. 위젯 사용 (기존 기능) ---
st.sidebar.header("도시 선택")
city = st.sidebar.text_input("도시 이름을 영어로 입력하세요", "Seoul")

if st.sidebar.button("날씨 정보 가져오기"):
    if not API_KEY.startswith("여기에"):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # --- 2. 데이터 표시 (기존 + '실습 3' 통계) ---
            st.subheader(f"🏙️ {data['name']}의 현재 날씨")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 기온", f"{data['main']['temp']} °C", f"{data['main']['feels_like']} °C 체감")
            col2.metric("💧 습도", f"{data['main']['humidity']} %")
            col3.metric("💨 풍속", f"{data['wind']['speed']} m/s")

            # --- [NEW] 실습 2/3 통합: 데이터 누적 ---
            # 현재 데이터를 딕셔너리로 정리
            current_data = {
                "도시": data['name'],
                "기온": data['main']['temp'],
                "습도": data['main']['humidity'],
                "풍속": data['wind']['speed'],
                "날씨": data['weather'][0]['description'],
                "수집 시간": datetime.fromtimestamp(data['dt'])
            }
            # 세션 기록에 추가
            st.session_state['history'].append(current_data)

        except requests.exceptions.HTTPError as err:
            if response.status_code == 401: st.error("API 키가 유효하지 않습니다.")
            elif response.status_code == 404: st.error(f"'{city}' 도시를 찾을 수 없습니다.")
            else: st.error(f"API 호출 중 오류 발생: {err}")
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
    else:
        st.warning("API 키를 입력해주세요.")

# --- [NEW] 실습 2/3 통합: 누적 데이터 시각화 (수정 완료) ---
if st.session_state['history']:
    st.subheader("📊 데이터 수집 기록")
    
    # 1. 전체 데이터를 데이터프레임으로 변환
    df = pd.DataFrame(st.session_state['history'])

    # --- 💡 [수정] 현재 사이드바의 'city' 값으로 데이터 필터링 ---
    city_df = df[df['도시'] == city] 
    
    # 2. 필터링된 데이터가 있는지 확인
    if not city_df.empty:
        st.info(f"'{city}' 도시의 누적 기록을 표시합니다.")
        
        # 3. 필터링된 데이터프레임 표시
        st.dataframe(city_df)

        # 4. 시각화 (꺾은선 그래프) - (💡 city_df 사용)
        st.subheader(f"📈 {city}의 시간에 따른 기온 및 습도 변화")
        fig = px.line(city_df, x='수집 시간', y=['기온', '습도'],
                      title=f"{city} 날씨 변화", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # 5. 기초 통계량 - (💡 city_df 사용)
        st.subheader(f"📈 {city}의 기초 통계량")
        st.dataframe(city_df[['기온', '습도', '풍속']].describe())

        # 6. CSV 다운로드 버튼 - (💡 city_df 사용)
        csv = city_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 {city} 데이터를 CSV로 다운로드",
            data=csv,
            file_name=f'{city}_weather_history.csv',
            mime='text/csv'
        )
    else:
        # (예외 처리) 전체 기록은 있으나, 현재 'city'로 조회된 기록은 없는 경우
        st.warning(f"'{city}' 도시에 대한 수집 기록이 아직 없습니다. 먼저 날씨 정보를 조회해주세요.")
    
    # (선택적) 전체 데이터 원본 표시
    with st.expander("🗂️ 전체 수집 기록 보기 (모든 도시)"):
        st.dataframe(df)
        
else:
    st.info("👆 사이드바에서 도시 날씨를 조회하면 기록이 시작됩니다.")

if st.session_state['history']:
    df = pd.DataFrame(st.session_state['history'])
    
    # 조회된 도시 목록 추출
    all_cities = df['도시'].unique()
    
    # 사이드바가 아닌 메인 화면에 selectbox 배치
    selected_city = st.selectbox("📈 기록을 볼 도시를 선택하세요", all_cities)
    
    # 선택된 도시로 필터링
    city_df = df[df['도시'] == selected_city]

    # (이하 로직은 city_df 사용으로 동일)
    st.subheader(f"📈 {selected_city}의 시간에 따른 기온 및 습도 변화")
    fig = px.line(city_df, ...)
    st.plotly_chart(fig)
    ...

# [추가 제안] 사이드바 하단
if st.sidebar.button("🗑️ 모든 기록 초기화"):
    st.session_state['history'] = [] # 혹은 'data_cache' = {}
    st.experimental_rerun() # 앱 즉시 새로고침
