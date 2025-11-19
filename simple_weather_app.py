# 주기적 데이터 수집 예제

import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "simple_weather.db"
COLLECTION_INTERVAL = 600  # 10분

DEFAULT_CITIES = ["Seoul", "Busan", "Jeju"]


def ensure_directories() -> None:
    """데이터 디렉토리 생성"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_resource
def init_db() -> None:
    """데이터베이스 초기화 (캐시 적용)"""
    ensure_directories()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temp REAL,
            humidity REAL,
            feels_like REAL
        )
        """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weather_city_time ON weather_records(city, timestamp)")
    conn.commit()
    conn.close()


def get_api_key() -> Optional[str]:
    """API 키 가져오기 (secrets 또는 환경변수)"""
    api_key = None
    if "openweather" in st.secrets and "api_key" in st.secrets["openweather"]:
        api_key = st.secrets["openweather"]["api_key"]
    elif "OPENWEATHER_API_KEY" in os.environ:
        api_key = os.environ["OPENWEATHER_API_KEY"]
    return api_key


@st.cache_data(ttl=COLLECTION_INTERVAL)
def fetch_weather(city: str) -> Dict:
    """OpenWeatherMap API에서 날씨 데이터 가져오기 (캐시 적용)"""
    api_key = get_api_key()
    if not api_key:
        st.warning("OPENWEATHER API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 또는 환경변수를 확인하세요.")
        raise RuntimeError("API key missing")

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "kr"}
    response = requests.get(base_url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def parse_weather(payload: Dict, city: str) -> Dict:
    """API 응답에서 필요한 데이터만 추출"""
    return {
        "city": city,
        "timestamp": datetime.now(UTC).isoformat(),
        "temp": payload["main"]["temp"],
        "humidity": payload["main"]["humidity"],
        "feels_like": payload["main"]["feels_like"],
    }


def save_weather(records: List[Dict]) -> None:
    """날씨 데이터를 SQLite에 저장"""
    if not records:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO weather_records (city, timestamp, temp, humidity, feels_like)
        VALUES (:city, :timestamp, :temp, :humidity, :feels_like)
        """,
        records,
    )
    conn.commit()
    conn.close()


def collect_weather(cities: List[str]) -> None:
    """선택된 도시들의 날씨 데이터 수집 및 저장"""
    records = []
    for city in cities:
        try:
            payload = fetch_weather(city)
            records.append(parse_weather(payload, city))
        except Exception:
            pass
    
    if records:
        save_weather(records)


@st.cache_data(ttl=COLLECTION_INTERVAL, show_spinner=False)
def get_latest_weather(cities: List[str]) -> List[Dict]:
    """최근 1시간 이내 데이터 중 각 도시별 마지막 데이터 조회 (캐시 적용)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    results = []
    
    placeholders = ",".join(["?"] * len(cities))
    cursor.execute(
        f"""
        SELECT w1.city, w1.timestamp, w1.temp, w1.humidity, w1.feels_like
        FROM weather_records w1
        INNER JOIN (
            SELECT city, MAX(timestamp) as max_timestamp
            FROM weather_records
            WHERE city IN ({placeholders}) AND timestamp >= ?
            GROUP BY city
        ) w2 ON w1.city = w2.city AND w1.timestamp = w2.max_timestamp
        ORDER BY w1.city
        """,
        cities + [cutoff_time],
    )
    
    for row in cursor.fetchall():
        results.append({
            "city": row[0],
            "timestamp": row[1],
            "temp": row[2],
            "humidity": row[3],
            "feels_like": row[4],
        })
    
    conn.close()
    return results


def display_dashboard(cities: List[str]) -> None:
    """대시보드 표시"""
    st.title("날씨 대시보드")
    
    weather_data = get_latest_weather(cities)
    
    if not weather_data:
        st.warning("최근 1시간 이내 데이터가 없습니다. 잠시 후 다시 시도해주세요.")
        return
    
    st.caption("최근 1시간 이내 수집된 최신 도시별 정보입니다.")
    
    for data in weather_data:
        with st.container():
            st.subheader(data["city"])
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("온도", f"{data['temp']:.1f} °C")
            with col2:
                st.metric("습도", f"{data['humidity']} %")
            with col3:
                st.metric("체감온도", f"{data['feels_like']:.1f} °C")
            
            timestamp = datetime.fromisoformat(data["timestamp"])
            st.caption(f"업데이트: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            st.divider()


def main():
    """메인 함수"""
    ensure_directories()
    init_db()
    
    st_autorefresh(interval=COLLECTION_INTERVAL * 1000, key="auto-refresh", limit=None)
    
    selected_cities = st.sidebar.multiselect(
        "도시 선택",
        options=DEFAULT_CITIES,
        default=DEFAULT_CITIES,
        help="날씨를 확인할 도시를 선택하세요."
    )
    
    if not selected_cities:
        st.warning("최소 한 개의 도시를 선택해주세요.")
        return
    
    collect_weather(selected_cities)
    display_dashboard(selected_cities)


if __name__ == "__main__":
    main()

