import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------------------------------------
# API KEY 설정
# ------------------------------------------------------------
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except KeyError:
    st.error("API 키가 Streamlit Secrets에 설정되지 않았습니다.")
    API_KEY = st.sidebar.text_input("🔑 로컬 실행용 API Key 입력", "")

st.set_page_config(page_title="날씨 모니터링 대시보드", page_icon="🌦️")
st.title("🌦️ 실시간 날씨 모니터링 대시보드")

# ------------------------------------------------------------
# 도시별 데이터 저장 구조
# ------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state["history"] = {}

# ------------------------------------------------------------
# 추천 활동 함수
# ------------------------------------------------------------
def get_activity_recommendation(weather):
    if "맑음" in weather:
        return "☀️ 맑은 날씨! 야외 활동 강추!"
    elif "비" in weather:
        return "🌧️ 비가 와요. 실내 활동 추천!"
    elif "눈" in weather:
        return "❄️ 눈이 옵니다! 따뜻하게 입고 외출하세요."
    elif "구름" in weather or "흐림" in weather:
        return "☁️ 흐린 날엔 카페·전시회 추천!"
    return "추천 활동 정보 없음"

def get_weather_icon(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


# ------------------------------------------------------------
# 사이드바 입력
# ------------------------------------------------------------
st.sidebar.header("도시 선택")
city_input = st.sidebar.text_input("도시 이름을 영어로 입력하세요", "Seoul")

# 입력값 정규화: 대소문자 상관없이 동일 도시로 저장
normalized_city = city_input.strip().lower().title()


# ------------------------------------------------------------
# 날씨 조회
# ------------------------------------------------------------
if st.sidebar.button("날씨 정보 가져오기"):

    if not API_KEY:
        st.warning("API Key를 입력해주세요.")
    else:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={normalized_city}&appid={API_KEY}&units=metric&lang=kr"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # 도시별 리스트 없으면 생성
            if normalized_city not in st.session_state["history"]:
                st.session_state["history"][normalized_city] = []

            # UI 표시
            st.subheader(f"🏙️ {data['name']}의 현재 날씨")
            st.image(get_weather_icon(data["weather"][0]["icon"]), width=90)

            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ 기온", f"{data['main']['temp']} °C", f"{data['main']['feels_like']} °C 체감")
            col2.metric("💧 습도", f"{data['main']['humidity']} %")
            col3.metric("💨 풍속", f"{data['wind']['speed']} m/s")

            # 추천
            weather_desc = data["weather"][0]["description"]
            st.info(f"✨ 활동 추천: {get_activity_recommendation(weather_desc)}")

            # 데이터 저장
            current_data = {
                "도시": data["name"],
                "기온": data["main"]["temp"],
                "습도": data["main"]["humidity"],
                "풍속": data["wind"]["speed"],
                "날씨": weather_desc,
                "수집 시간": datetime.fromtimestamp(data["dt"])
            }

            # 최신순 저장
            st.session_state["history"][normalized_city].insert(0, current_data)

        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                st.error("API Key가 유효하지 않습니다.")
            elif response.status_code == 404:
                st.error(f"'{city_input}' 도시를 찾을 수 없습니다.")
            else:
                st.error(f"API 오류: {err}")
        except Exception as e:
            st.error(f"데이터 처리 오류: {e}")

# ------------------------------------------------------------
# 전체 데이터 + Tabs
# ------------------------------------------------------------
if st.session_state["history"]:

    # 전체 데이터
    all_rows = []
    for c, items in st.session_state["history"].items():
        all_rows.extend(items)

    df_all = pd.DataFrame(all_rows)
    st.subheader("📊 전체 데이터 기록")
    st.dataframe(df_all, use_container_width=True)

    csv_all = df_all.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 전체 CSV 다운로드", data=csv_all, file_name="all_weather_history.csv")

    st.divider()

    # Tabs 생성
    tabs = st.tabs(st.session_state["history"].keys())

    # 각 city별 Tab UI
    for tab, city_name in zip(tabs, st.session_state["history"].keys()):
        with tab:
            st.write(f"### 🌍 {city_name} 수집 데이터")

            city_df = pd.DataFrame(st.session_state["history"][city_name])
            st.dataframe(city_df)

            # 그래프 (DuplicateElementId 방지 → key 부여)
            st.subheader("📈 기온 및 습도 변화")
            fig = px.line(city_df, x="수집 시간", y=["기온", "습도"], markers=True)
            st.plotly_chart(fig, use_container_width=True, key=f"{city_name}_chart")

            st.subheader("📊 기초 통계량")
            st.dataframe(city_df[["기온", "습도", "풍속"]].describe())

            # CSV 다운로드
            csv_city = city_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                f"📥 {city_name} CSV 다운로드",
                data=csv_city,
                file_name=f"{city_name}_weather.csv",
                mime="text/csv"
            )

else:
    st.info("👆 도시를 입력하고 조회 버튼을 눌러주세요!")


# ------------------------------------------------------------
# 기록 초기화
# ------------------------------------------------------------
if st.sidebar.button("🗑️ 모든 기록 초기화"):
    st.session_state["history"] = {}
    st.rerun()
