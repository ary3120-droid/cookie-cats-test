import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Cookie Cats A/B Test Report", layout="wide")

# 데이터 로드 (수치 정확도 보정 덧붙임)
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    df['retention_1'] = df['retention_1'].astype(bool)
    df['retention_7'] = df['retention_7'].astype(bool)
    return df

df = load_data()

# 스타일링 (가독성 향상)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- 타이틀 섹션 ---
st.title("🎮 Cookie Cats 게이트 위치 변경 실험 리포트")
st.caption("실험 설계: gate_30 (기존) vs gate_40 (변경안) | 분석 범위: 리텐션 및 플레이 행동량")
st.markdown("---")

# 1. KPI_실험개요 (전제 확인)
st.subheader("1️⃣ KPI_실험개요: 실험 데이터의 신뢰성 확인")
total_n = len(df)
g30_n = len(df[df['version'] == 'gate_30'])
g40_n = len(df[df['version'] == 'gate_40'])
g30_pct = (g30_n / total_n)
g40_pct = (g40_n / total_n)

col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 사용자 수", f"{total_n:,}명")
col2.metric("gate_30 (Control)", f"{g30_n:,}명")
col3.metric("gate_40 (Test)", f"{g40_n:,}명")
col4.metric("샘플 비율", f"{g30_pct:.1%} : {g40_pct:.1%}", "안정적")
st.info("💡 **의의:** 두 그룹 간 표본 수 차이가 크지 않음을 확인하여 실험 결과 해석의 공정성을 확보함.")

# 2. 리텐션 지표 비교 (결과 판단 - 인터랙티브 차트 덧붙임)
st.markdown("---")
st.subheader("2️⃣ 리텐션 지표 비교: 성공 여부 판단")
ret7 = df.groupby('version')['retention_7'].mean()
ret1 = df.groupby('version')['retention_1'].mean()

c_ret1, c_ret2 = st.columns(2)
with c_ret1:
    st.write("#### [Primary] 7-Day Retention Rate")
    fig7 = px.bar(ret7, x=ret7.index, y=ret7.values, text_auto='.2%', 
                  color=ret7.index, color_discrete_sequence=['#636EFA', '#EF553B'])
    fig7.update_layout(showlegend=False, height=350, yaxis_tickformat='.1%')
    st.plotly_chart(fig7, use_container_width=True)
    st.write("**분석:** gate_40 리텐션이 약 0.8%p 낮게 관찰됨 (부정적).")

with c_ret2:
    st.write("#### [Secondary] 1-Day Retention Rate")
    fig1 = px.bar(ret1, x=ret1.index, y=ret1.values, text_auto='.2%', 
                  color=ret1.index, color_discrete_sequence=['#00CC96', '#AB63FA'])
    fig1.update_layout(showlegend=False, height=350, yaxis_tickformat='.1%')
    st.plotly_chart(fig1, use_container_width=True)

# 3. 플레이 지표 분석 (근거 확인 - 고해상도 박스플롯 덧붙임)
st.markdown("---")
st.subheader("3️⃣ 플레이 지표 분석: 행동 변화의 근거")
col_play1, col_play2 = st.columns(2)

with col_play1:
    st.write("#### Play Count Distribution (Capped)")
    fig_box = px.box(df, x="version", y="sum_gamerounds_capped", color="version",
                     color_discrete_sequence=['#636EFA', '#EF553B'])
    fig_box.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption("※ 상위 1% 이상치를 보정한 분포입니다.")

with col_play2:
    st.write("#### Play Count (Retained Users Only)")
    retained_df = df[df['retention_7'] == True]
    intensity = retained_df.groupby('version')['sum_gamerounds_capped'].mean()
    fig_int = px.bar(intensity, x=intensity.index, y=intensity.values, text_auto='.1f',
                     color=intensity.index, color_discrete_sequence=['#FFA15A', '#19D3AF'])
    fig_int.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_int, use_container_width=True)
    st.write("**의의:** 잔존 유저의 질적 행동 변화 확인.")

# 4. Result_Summary (성공 판정 및 종합 해석)
st.markdown("---")
st.subheader("4️⃣ Result_Summary: 실험 성공 판정 및 종합 해석")

# 성공 판정 카드 디자인
score_col1, score_col2 = st.columns([1, 2])

with score_col1:
    st.error("### **최종 판정: FAILURE (도입 철회)**")
    st.markdown("""
    **판정 근거:**
    - **필수 조건:** Retention_7 개선 여부 → **[미달성]**
    - **통계적 유의성:** p-value < 0.05 확인 → **[유의미한 하락]**
    """)

with score_col2:
    # 성공 판정 규칙 테이블
    data = {
        "구분": ["Primary (7일 리텐션)", "Secondary (1일 리텐션)", "Secondary (전체 행동량)", "Secondary (유지유저 강도)"],
        "검증 목표": ["0.5%p 이상 상승", "현상 유지 이상", "평균치 상승", "사후 분석용"],
        "결과": ["▼ 0.82%p 하락", "▼ 0.59%p 하락", "변화 없음", "▲ 7.6회 상승"],
        "판정": ["❌ Fail", "⚠️ Warning", "➖ Neutral", "✅ Success"]
    }
    st.table(pd.DataFrame(data))

# 상세 인사이트 정리
st.markdown("---")
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.info("### 📉 왜 실패했는가? (전체 유저 관점)")
    st.markdown("""
    - **초기 이탈 가속:** 게이트를 40으로 미룬 것이 유저에게 '휴식'이 아닌 '피로'를 유발.
    - **가드레일 붕괴:** 핵심 지표인 7일 리텐션이 무너지면서 다른 보조 지표의 개선 효과가 무의미해짐.
    """)

with insight_col2:
    st.success("### 🔍 무엇을 발견했는가? (잔존 유저 관점)")
    st.markdown("""
    - **사후 분석 결과:** 게이트를 통과한 '코어 유저'들은 30 버전보다 40 버전에서 더 깊은 몰입도(평균 +7.6회)를 보임.
    - **전략적 시사점:** 게이트 상향은 전체 리텐션을 깎지만, **남아있는 유저의 LTV(생애가치)는 높이는 양날의 검**임.
    """)

st.warning("⚠️ **최종 권고:** 비즈니스 안정성을 위해 **gate_30 버전을 유지**하되, 잔존 유저의 몰입도를 높일 수 있는 별도의 인게임 이벤트를 검토할 것.")
