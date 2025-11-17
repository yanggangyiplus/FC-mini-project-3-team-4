import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📁 CSV 파일 분석기")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=['csv'])

if uploaded_file is not None:
    # 데이터 읽기
    df = pd.read_csv(uploaded_file)
    st.success("✅ 파일 업로드 성공!")

    # 기본 정보
    st.subheader("📊 데이터 기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**행 개수:** {len(df)}")
        st.write(f"**열 개수:** {len(df.columns)}")
    with col2:
        st.write(f"**컬럼:** {', '.join(df.columns)}")

    # 데이터 미리보기
    st.subheader("🔍 데이터 미리보기")
    st.dataframe(df.head(10))

    # 기초 통계
    st.subheader("📈 기초 통계량")
    st.dataframe(df.describe())

    # 컬럼 선택 및 시각화
    st.subheader("📊 시각화")
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) > 0:
        selected_col = st.selectbox("시각화할 컬럼 선택", numeric_cols)
        fig = px.histogram(df, x=selected_col, title=f'{selected_col} 분포')
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👆 CSV 파일을 업로드해주세요!")

    # 샘플 데이터 다운로드
    st.subheader("💾 샘플 데이터 다운로드")
    sample_df = pd.DataFrame({
        '이름': ['철수', '영희', '민수', '지영'],
        '나이': [25, 30, 28, 32],
        '점수': [85, 92, 78, 95]
    })
    csv = sample_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 샘플 CSV 다운로드",
        data=csv,
        file_name='sample_data.csv',
        mime='text/csv'
    )
