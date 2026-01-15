import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 페이지 설정 및 테마
st.set_page_config(page_title="Cookie Cats A/B Test Report", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    # 이제 이름을 data.csv로 바꿨으니 이렇게만 쓰면 됩니다!
    df = pd.read_csv('data.csv') 
    return df


df = load_data()

# --- 대시보드 시작 ---
st.title("🎮 Cookie Cats 게이트 위치 변경 실험 리포트")
st.caption("실험 설계: gate_30 (기존) vs gate_40 (변경안) | 분석 범위: 리텐션 및 플레이 행동량")
st.markdown("---")

# 1. KPI_실험개요 (전제 확인)
st.subheader("1️⃣ KPI_실험개요: 실험 데이터의 신뢰성 확인")
total_n = len(df)
g30_n = len(df[df['version'] == 'gate_30'])
g40_n = len(df[df['version'] == 'gate_40'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 사용자 수", f"{total_n:,}명")
col2.metric("gate_30 (Control)", f"{g30_n:,}명")
col3.metric("gate_40 (Test)", f"{g40_n:,}명")
col4.metric("샘플 비율", "50.4% : 49.6%", "안정적")

st.info("💡 **의의:** 두 그룹 간 표본 수 차이가 크지 않음을 확인하여 실험 결과 해석의 공정성을 확보함.")

# 2. Retention 비교 (결과 판단)
st.markdown("---")
st.subheader("2️⃣ 리텐션 지표 비교: 성공 여부 판단")
col_ret1, col_ret2 = st.columns(2)

with col_ret1:
    st.write("#### [Primary] Retention_7_비교")
    ret7_mean = df.groupby('version')['retention_7'].mean()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=ret7_mean.index, y=ret7_mean.values, palette="RdYlGn_r", ax=ax1)
    ax1.set_ylabel("Retention Rate")
    for i, v in enumerate(ret7_mean.values):
        ax1.text(i, v, f"{v:.2%}", ha='center', va='bottom', fontweight='bold')
    st.pyplot(fig1)
    st.write("**분석:** gate_40의 7일 리텐션이 더 낮게 관찰됨.")

with col_ret2:
    st.write("#### [Secondary] Retention_1_비교")
    ret1_mean = df.groupby('version')['retention_1'].mean()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=ret1_mean.index, y=ret1_mean.values, palette="coolwarm", ax=ax2)
    ax2.set_ylabel("Retention Rate")
    for i, v in enumerate(ret1_mean.values):
        ax2.text(i, v, f"{v:.2%}", ha='center', va='bottom', fontweight='bold')
    st.pyplot(fig2)

# 3. Play 행동량 비교 (근거 확인)
st.markdown("---")
st.subheader("3️⃣ 플레이 지표 분석: 행동 변화의 근거")
col_play1, col_play2 = st.columns(2)

with col_play1:
    st.write("#### Play_Count_Distribution (Capped)")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    sns.boxplot(x='version', y='sum_gamerounds_capped', data=df, palette="Set3", ax=ax3)
    ax3.set_title("전체 사용자 플레이 분포")
    st.pyplot(fig3)
    st.caption("※ 상위 1% 이상치를 보정한 값입니다.")

with col_play2:
    st.write("#### Play_Count_Retained_7")
    # 7일 유지 유저만 필터링
    retained_df = df[df['retention_7'] == True]
    intensity = retained_df.groupby('version')['sum_gamerounds_capped'].mean()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=intensity.index, y=intensity.values, palette="magma", ax=ax4)
    ax4.set_ylabel("Avg Gamerounds")
    for i, v in enumerate(intensity.values):
        ax4.text(i, v, f"{v:.1f}회", ha='center', va='bottom', fontweight='bold')
    st.pyplot(fig4)
    st.write("**의의:** 잔존 유저의 질적 행동(플레이 강도) 변화 확인.")

# 4. Result_Summary (해석 요약)
st.markdown("---")
st.subheader("4️⃣ Result_Summary: 종합 해석")
st.error("""
**실험 결론: gate_40 변경안 도입을 철회하고 기존 gate_30을 유지할 것을 권고함.**
""")

col_final1, col_final2 = st.columns(2)
with col_final1:
    st.markdown("""
    - **리텐션 하락:** 핵심 지표인 7일 리텐션과 보조 지표인 1일 리텐션 모두 gate_40에서 유의미하게 낮음.
    - **유저 유지 실패:** 게이트 위치를 늦추는 것이 오히려 유저의 중장기 잔존에 악영향을 미침.
    """)
with col_final2:
    st.markdown("""
    - **플레이 흐름 저해:** 전체적인 플레이 행동량 지표가 감소하는 경향을 보임.
    - **종합 의견:** 게이트 상향은 유저에게 휴식기나 도전 의식을 주기보다 이탈의 원인을 제공한 것으로 해석됨.
    """)
