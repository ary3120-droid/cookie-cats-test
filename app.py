import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 (다크 테마 느낌의 스타일)
st.set_page_config(page_title="Cookie Cats Executive Report", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    df['retention_1'] = df['retention_1'].astype(bool)
    df['retention_7'] = df['retention_7'].astype(bool)
    return df

df = load_data()

# 커스텀 스타일 입히기
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 타이틀 섹션 ---
st.title("📊 Cookie Cats A/B Test Dashboard")
st.subheader("Gate Location: 30 vs 40 Analysis")
st.markdown("---")

# 1. 핵심 지표 (KPI) - 가독성 극대화
ret7 = df.groupby('version')['retention_7'].mean()
ret1 = df.groupby('version')['retention_1'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    diff7 = (ret7['gate_40'] - ret7['gate_30']) / ret7['gate_30']
    st.metric("7-Day Retention (Primary)", f"{ret7['gate_40']:.2%}", f"{diff7:.2%} vs gate_30", delta_color="inverse")
with col2:
    diff1 = (ret1['gate_40'] - ret1['gate_30']) / ret1['gate_30']
    st.metric("1-Day Retention (Secondary)", f"{ret1['gate_40']:.2%}", f"{diff1:.2%} vs gate_30", delta_color="inverse")
with col3:
    st.metric("Total Sample Size", f"{len(df):,} Users", "Stable State")

st.markdown("---")

# 2. 리텐션 분석 (Plotly 인터랙티브 차트)
c1, c2 = st.columns(2)
with c1:
    st.markdown("#### 📍 7-Day Retention Rate")
    fig7 = px.bar(ret7, x=ret7.index, y=ret7.values, color=ret7.index, 
                  text_auto='.2%', color_discrete_sequence=['#636EFA', '#EF553B'])
    fig7.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig7, use_container_width=True)

with c2:
    st.markdown("#### 📍 1-Day Retention Rate")
    fig1 = px.bar(ret1, x=ret1.index, y=ret1.values, color=ret1.index, 
                  text_auto='.2%', color_discrete_sequence=['#00CC96', '#AB63FA'])
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

# 3. 플레이 분포 (박스플롯 업그레이드)
st.markdown("---")
st.markdown("#### 🎮 Play Count Distribution (Capped at 99th Percentile)")
fig_box = px.box(df, x="version", y="sum_gamerounds_capped", color="version",
                 points="outliers", notched=True,
                 color_discrete_sequence=['#636EFA', '#EF553B'])
fig_box.update_layout(height=500)
st.plotly_chart(fig_box, use_container_width=True)

# 4. 종합 결론 섹션 (가장 멋지게)
st.markdown("---")
st.success("### 📝 최종 분석 요약 및 권고")
res_col1, res_col2 = st.columns([2, 1])
with res_col1:
    st.markdown("""
    * **핵심 결과:** 게이트 위치를 40으로 상향 시, **7일 리텐션이 약 0.8%p 유의미하게 하락**함.
    * **행동 변화:** 플레이 횟수의 중앙값은 큰 차이가 없으나, 상위 유저의 유지력이 약화됨.
    * **비즈니스 임팩트:** 유저 이탈로 인한 장기적 매출 감소 위험 존재.
    """)
with res_col2:
    st.error("#### 🚫 결론: Rollback Recommended")
    st.write("기존 gate_30 버전 유지가 유저 잔존율 측면에서 훨씬 유리합니다.")
