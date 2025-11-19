# 🌦️ 4조 실시간 날씨 모니터링 대시보드 (Weather Dashboard)


## 📖 프로젝트 소개
OpenWeatherMap API를 활용하여 사용자가 입력한 도시의 실시간 날씨 정보를 조회하고, 
데이터를 누적하여 시각화하는 웹 애플리케이션입니다.
Streamlit을 사용하여 빠르고 직관적인 대시보드를 구축했습니다.


## 🚀 주요 기능
- **실시간 날씨 조회:** 도시명 입력 시 기온, 습도, 풍속, 날씨 상태 아이콘 표시
- **활동 추천:** 날씨 상태(맑음, 비, 눈 등)에 따른 맞춤형 활동 멘트 제공
- **데이터 시각화:** 조회한 도시의 기온/습도 변화를 Plotly 라인 차트로 시각화
- **이력 관리:** 조회된 데이터를 세션에 저장하고 CSV 파일로 다운로드 제공


## 🛠️ 기술 스택 (Tech Stack)
- **Language:** Python 3.x
- **Framework:** Streamlit
- **Data Analysis:** Pandas
- **Visualization:** Plotly Express
- **API:** OpenWeatherMap API


## 📦 설치 및 실행 방법 (Installation)

1. 레포지토리 클론
   ```bash
   git clone [레포지토리 주소]

2. 필수 라이브러리 설치
   ```bash
    pip install streamlit requests pandas plotly

3. API 키 설정
   ```bash
   .streamlit/secrets.toml 파일을 생성하거나, 앱 실행 후 사이드바에 키를 직접 입력하세요.
   
4. 앱 실행
   ```bash
   streamlit run app.py


📂 데이터 샘플
도시,기온,습도,날씨
Seoul,24.5°C,45%,☀️ 맑음
Tokyo,22.1°C,60%,🌧️ 비

