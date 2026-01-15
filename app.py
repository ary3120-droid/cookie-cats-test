import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="Cookie Cats Report", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    # True/False가 글자로 인식될 경우를 대비해 불리언으로 강제 변환
    df['retention_1'] = df['retention_1'].astype(bool)
    df['retention_7'] = df['retention_7'].astype(bool)
    return df

df = load_data()

# 데이터가 잘 들어왔는지 확인용 (상단에 작게 표시)
st.sidebar.write(f"📊 로드된 데이터: {len(df):,}행")

st.title("🎮 Cookie Cats A/B 테스트 리포트")
st.markdown("---")

# 1. KPI 섹션
col1, col2, col3 = st.columns(3)
ret7 = df.groupby('version')['retention_7'].mean()
ret1 = df.groupby('version')['retention_1'].mean()

with col1:
    st.metric("7일 리텐션 (gate_30)", f"{ret7['gate_30']:.2%}")
    st.metric("7일 리텐션 (gate_40)", f"{ret7['gate_40']:.2%}", f"{ret7['gate_40']-ret7['gate_30']:.2%}", delta_color="inverse")

with col2:
    st.metric("1일 리텐션 (gate_30)", f"{ret1['gate_30']:.2%}")
    st.metric("1일 리텐션 (gate_40)", f"{ret1['gate_40']:.2%}", f"{ret1['gate_40']-ret1['gate_30']:.2%}", delta_color="inverse")

with col3:
    st.warning("### 최종 권고")
    st.subheader("🚩 gate_30 유지")

# 2. 시각화 섹션
st.subheader("📈 상세 지표 비교")
tab1, tab2 = st.tabs(["리텐션 분포", "플레이 횟수"])

with tab1:
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    df.groupby('version')['retention_7'].mean().plot(kind='bar', color=['skyblue', 'salmon'], ax=ax1)
    ax1.set_title("7 Day Retention Rate by Version")
    st.pyplot(fig1)

with tab2:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.boxplot(x='version', y='sum_gamerounds_capped', data=df, ax=ax2)
    ax2.set_title("Gamerounds Distribution (Capped)")
    st.pyplot(fig2)
