import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="데이터 시각화 앱", page_icon="📊")

st.title("📊 4조팀프로젝트 대시보드")

st.sidebar.header("설정")
st.sidebar.write("👈 슬라이더를 움직여보세요!")
num_points = st.sidebar.slider("데이터 포인트 수", 20, 200, 100)

@st.cache_data
def generate_data(n):
    return pd.DataFrame({
        'x': np.random.randn(n),
        'y': np.random.randn(n),
        'category': np.random.choice(['행복', '슬픔', '멋짐'], n)
    })

df = generate_data(num_points)

st.subheader("📋 데이터 미리보기")
st.dataframe(df.head())

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("평균 X", f"{df['x'].mean():.2f}")

with col2:
    st.metric("평균 Y", f"{df['y'].mean():.2f}")

with col3:
    st.metric("총 데이터", len(df))

st.subheader("📈 산점도")
fig = px.scatter(df, x='x', y='y', color='category', title='랜덤 데이터 분포'
color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#95E1D3'])
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 분포 히스토그램")
chart_type = st.selectbox("변수 선택", ['x', 'y'])
fig2 = px.histogram(df, x=chart_type, nbins=20, title=f'{chart_type} 분포')
st.plotly_chart(fig2, use_container_width=True)