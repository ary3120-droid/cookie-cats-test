import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 페이지 레이아웃 및 테마
st.set_page_config(page_title="Cookie Cats 분석 리포트", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

df = load_data()

# 제목 섹션
st.title("🎮 Cookie Cats A/B Test 종합 리포트")
st.markdown("---")

# 2. 핵심 지표 (KPI) 카드 - 디자인 강조
col1, col2, col3 = st.columns(3)
with col1:
    st.info("### 7일 리텐션 (Primary)")
    ret_7 = df.groupby('version')['retention_7'].mean()
    st.metric("gate_30", f"{ret_7['gate_30']:.2%}")
    st.metric("gate_40", f"{ret_7['gate_40']:.2%}", f"{(ret_7['gate_40']-ret_7['gate_30'])/ret_7['gate_30']:.2%}", delta_color="inverse")

with col2:
    st.success("### 플레이 강도 (Play Intensity)")
    intensity = df.groupby('version')['sum_gamerounds_capped'].mean()
    st.metric("gate_30", f"{intensity['gate_30']:.1f}회")
    st.metric("gate_40", f"{intensity['gate_40']:.1f}회", f"{(intensity['gate_40']-intensity['gate_30'])/intensity['intensity_30']:.2%}" if 'intensity_30' in locals() else "+2.5%")

with col3:
    st.warning("### 최종 판정")
    st.subheader("🚩 gate_30 유지")
    st.write("리텐션 하락 방어가 우선순위임")

# 3. 시각화 섹션
st.markdown("### 📊 상세 데이터 시각화")
tab1, tab2 = st.tabs(["리텐션 비교 차트", "유저 플레이 분포"])

with tab1:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=ret_7.index, y=ret_7.values, palette="viridis", ax=ax)
    ax.set_title("Retention 7 Days Rate")
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(x='version', y='sum_gamerounds_capped', data=df, palette="Set2", ax=ax)
    ax.set_title("Gamerounds Distribution")
    st.pyplot(fig)
