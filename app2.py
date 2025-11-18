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
    API_KEY = "local_test_key"  # 로컬 테스트용 키

st.set_page_config(page_title="날씨 모니터링 대시보드", page_icon="🌦️")
st.title("🌦️ 실시간 날씨 모니터링 대시보드")

# --- [NEW] 도시별 데이터 저장을 위한 구조 변경 ---
# 기존: history → 리스트
# 변경: 도시 이름을 key로 가지는 dict 형태
if "history" not in st.session_state:
    st.session_state["history"] = {}  # 예: {"Seoul": [...], "Busan": [...]}

# --- 1. 위젯 사용 ---
st.sidebar.header("도시 선택")
city = st.sidebar.text_input("도시 이름을 영어로 입력하세요", "Seoul")

# --- [NEW] 날씨별 활동 추천 함수 ---
def get_activity_recommendation(weather):
    if "맑음" in weather:
        return "☀️ 맑은 날씨예요! 야외 산책이나 공원 나들이를 추천드려요."
    elif "비" in weather:
        return "🌧️ 비가 옵니다! 실내에서 카페, 영화 감상 등을 추천드려요."
    elif "눈" in weather:
        return "❄️ 눈이 와요! 따뜻하게 입고 눈 구경 산책 어때요?"
    elif "구름" in weather or "흐림" in weather:
        return "☁️ 흐린 날엔 실내 운동이나 독서, 전시 관람도 좋아요."
    else:
        return "현재 날씨에 맞는 추천 활동 정보를 찾지 못했어요."

# --- [NEW] 벡터 이미지(아이콘) URL 생성 함수 ---
def get_weather_icon(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

# --- 데이터 수집 버튼 ---
if st.sidebar.button("날씨 정보 가져오기"):
    if not API_KEY.startswith("여기에"):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # 도시 이름 키가 존재하지 않으면 초기화
            if city not in st.session_state["history"]:
                st.session_state["history"][city] = []

            # --- 2. 데이터 표시 ---
            st.subheader(f"🏙️ {data['name']}의 현재 날씨")

            # 날씨 아이콘 표시
            icon_code = data["weather"][0]["icon"]
            st.image(get_weather_icon(icon_code), width=90)

            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 기온", f"{data['main']['temp']} °C", f"{data['main']['feels_like']} °C 체감")
            col2.metric("💧 습도", f"{data['main']['humidity']} %")
            col3.metric("💨 풍속", f"{data['wind']['speed']} m/s")

            # 추천 활동 표시
            weather_desc = data["weather"][0]["description"]
            st.info(f"✨ 활동 추천: {get_activity_recommendation(weather_desc)}")

            # --- [NEW] 도시별 데이터 누적 ---
            current_data = {
                "도시": data["name"],
                "기온": data["main"]["temp"],
                "습도": data["main"]["humidity"],
                "풍속": data["wind"]["speed"],
                "날씨": weather_desc,
                "수집 시간": datetime.fromtimestamp(data["dt"])
            }

            st.session_state["history"][city].append(current_data)

        except requests.exceptions.HTTPError as err:
            if response.status_code == 401: st.error("API 키가 유효하지 않습니다.")
            elif response.status_code == 404: st.error(f"'{city}' 도시를 찾을 수 없습니다.")
            else: st.error(f"API 호출 중 오류 발생: {err}")
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
    else:
        st.warning("API 키를 입력해주세요.")

# --- [NEW] 도시별 Tab 대시보드 ---
if st.session_state["history"]:
    st.subheader("📊 도시별 데이터 기록")

    # Tab으로 도시 구분
    tabs = st.tabs(st.session_state["history"].keys())

    for tab, city_name in zip(tabs, st.session_state["history"].keys()):
        with tab:
            st.write(f"### 🌍 {city_name} 수집 데이터")

            df = pd.DataFrame(st.session_state["history"][city_name])
            st.dataframe(df)

            # --- 시각화 ---
            st.subheader("📈 기온 및 습도 변화")
            fig = px.line(df, x="수집 시간", y=["기온", "습도"],
                          title=f"{city_name} 변화 추이", markers=True)
            st.plotly_chart(fig, use_container_width=True)

            # --- 기초 통계 ---
            st.subheader("📊 기초 통계량")
            st.dataframe(df[["기온", "습도", "풍속"]].describe())

            # --- CSV 다운로드 ---
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label=f"📥 {city_name} 데이터 CSV 다운로드",
                data=csv,
                file_name=f"{city_name}_weather_history.csv",
                mime="text/csv"
            )
else:
    st.info("👆 사이드바에서 도시 날씨를 조회하면 기록이 시작됩니다.")
