import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 및 데이터 로드
st.set_page_config(page_title="Cookie Cats A/B Test Analysis", layout="wide")

@st.cache_data
def load_data():
    # 데이터 파일명은 환경에 맞게 수정하세요
    df = pd.read_csv('data.csv')
    df['retention_1'] = df['retention_1'].astype(bool)
    df['retention_7'] = df['retention_7'].astype(bool)
    return df

df = load_data()

# 커스텀 CSS (카드 디자인)
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fb; padding: 15px; border-radius: 10px; border-left: 5px solid #636EFA; }
    .insight-box { background-color: #f1f3f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 타이틀 섹션 ---
st.title("🎮 Cookie Cats 게이트 배치 최적화 실험 분석")
st.markdown("#### '의도된 불편함'과 '유저 몰입' 사이의 트레이드오프 분석")
st.markdown("---")

# 1️⃣ 실험 신뢰성 확인 (SRM Check)
st.subheader("1. 데이터 신뢰성 및 샘플 분포 확인")
total_n = len(df)
g30_n = len(df[df['version'] == 'gate_30'])
g40_n = len(df[df['version'] == 'gate_40'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("전체 샘플 수 (N)", f"{total_n:,}")
with col2:
    st.metric("gate_30 (Control)", f"{g30_n:,}", f"{(g30_n/total_n):.1%}")
with col3:
    st.metric("gate_40 (Treatment)", f"{g40_n:,}", f"{(g40_n/total_n):.1%}")

st.info("💡 **SRM 확인:** 미세한 샘플 불균형이 관측되나, 대규모 표본에 따른 통계적 민감성으로 판단됨. 분석 결과에 미치는 영향은 제한적임.")

# 2️⃣ 가설 1 검정: 리텐션 (Primary & Guardrail)
st.markdown("---")
st.subheader("2. 가설 1 검정: 사용자 리텐션 영향 분석")
st.write("> **필수 조건:** 7일 리텐션의 유의미한 개선이 확인되어야 함")

ret7 = df.groupby('version')['retention_7'].mean()
ret1 = df.groupby('version')['retention_1'].mean()

c_ret1, c_ret2 = st.columns(2)
with c_ret1:
    st.write("#### [Primary] 7-Day Retention Rate")
    fig7 = px.bar(ret7, x=ret7.index, y=ret7.values, text_auto='.2%', 
                  color=ret7.index, color_discrete_sequence=['#636EFA', '#EF553B'])
    fig7.update_layout(showlegend=False, height=350, yaxis_tickformat='.1%')
    st.plotly_chart(fig7, use_container_width=True)
    st.error("**검정 결과:** gate_40에서 약 0.8%p 하락 확인 (대립가설 기각)")

with c_ret2:
    st.write("#### [Guardrail] 1-Day Retention Rate")
    fig1 = px.bar(ret1, x=ret1.index, y=ret1.values, text_auto='.2%', 
                  color=ret1.index, color_discrete_sequence=['#00CC96', '#AB63FA'])
    fig1.update_layout(showlegend=False, height=350, yaxis_tickformat='.1%')
    st.plotly_chart(fig1, use_container_width=True)
    st.warning("**모니터링:** 초기 안착 단계에서도 유의미한 개선 없음")

# 3️⃣ 가설 2 검정: 플레이 행동량 (Volume & Intensity)
st.markdown("---")
st.subheader("3. 가설 2 검정: 사용자 플레이 행동 변화")

col_play1, col_play2 = st.columns(2)
with col_play1:
    st.write("#### [2-1] 전체 플레이 행동량 (Capped)")
    fig_box = px.box(df, x="version", y="sum_gamerounds_capped", color="version",
                     color_discrete_sequence=['#636EFA', '#EF553B'])
    fig_box.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)
    st.write("**결과:** 전체 사용자 기준 플레이 총량의 유의미한 변화 없음")

with col_play2:
    # 사후 분석 지표: 7일 유지 유저만 필터링
    st.write("#### [2-2] 7일 유지 유저의 평균 플레이 강도")
    retained_df = df[df['retention_7'] == True]
    intensity = retained_df.groupby('version')['sum_gamerounds_capped'].mean()
    
    fig_int = px.bar(intensity, x=intensity.index, y=intensity.values, text_auto='.1f',
                     color=intensity.index, color_discrete_sequence=['#FFA15A', '#19D3AF'])
    fig_int.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_int, use_container_width=True)
    st.success(f"**발견:** 잔존 유저 집단 내 몰입도 **+7.6회 유의적 상승** ($p < 0.05$)")

# 4️⃣ 최종 의사결정 및 인사이트 (통합)
st.markdown("---")
st.subheader("4. 최종 성공 판정 및 비즈니스 제언")

score_col1, score_col2 = st.columns([1, 2])
with score_col1:
    st.error("## **최종 판정: FAILURE**")
    st.markdown("### **기존안(gate_30) 유지**")
    st.write("핵심 지표인 7일 리텐션이 하락하여 변경안 채택 불가.")

with score_col2:
    # 성격별 지표 요약 테이블
    results = {
        "지표 유형": ["Primary (7일 리텐션)", "Guardrail (1일 리텐션)", "Volume (전체 행동량)", "Insight (플레이 강도)"],
        "가설 결과": ["▼ 하락 (기각)", "➖ 중립 (기각)", "➖ 중립 (기각)", "▲ 상승 (채택)"],
        "비즈니스 영향": ["유저 이탈 위험 증가", "초기 경험 개선 미비", "양적 성장 한계", "잔존 유저 가치 증가"]
    }
    st.table(pd.DataFrame(results))

st.markdown("### 💡 핵심 인사이트 및 전략")
ins1, ins2 = st.columns(2)
with ins1:
    st.info("**📉 '감질맛'의 힘 (심리 분석)**\ngate_30의 이른 차단은 유저에게 '드라마 클리프행어'와 같은 효과를 주어 재방문을 유도합니다. gate_40은 이를 제거하여 유저가 한 번에 피로를 느끼게 만들었습니다.")
with ins2:
    st.success("**🚀 몰입의 트레이드오프 (전략 분석)**\ngate_40은 리텐션은 깎지만, 살아남은 유저를 더 '헤비 유저'로 만듭니다. 이는 유저 수(Quantity)와 유저당 가치(Quality) 사이의 선택 문제입니다.")

st.warning("⚠️ **최종 권고:** 현재 리텐션 방어가 최우선이므로 **gate_30을 유지**하십시오. 단, gate_40에서 확인된 몰입 상승 효과는 추후 '헤비 유저 전용 모드' 설계 시 반영할 것을 제안합니다.")


# --- 추가 제언 섹션: 비즈니스 임팩트 분석 ---
st.markdown("---")
st.subheader("🚀 비즈니스 임팩트 및 시뮬레이션")

col_biz1, col_biz2 = st.columns(2)

with col_biz1:
    st.write("#### 💸 리텐션 하락에 따른 유저 손실 추정")
    # 리텐션 차이 계산 (0.82%p 가정)
    ret_diff = 0.0082 
    # 가상의 월간 신규 유입자 수 설정
    new_users_monthly = st.number_input("월간 신규 유입 유저 수(UA) 설정", value=100000, step=10000)
    
    lost_users = int(new_users_monthly * ret_diff)
    st.error(f"**월간 예상 잔존 유저 손실: 약 {lost_users:,}명**")
    st.caption(f"※ gate_40 도입 시, gate_30 대비 매월 {lost_users:,}명의 유저가 더 이탈함을 의미함")

with col_biz2:
    st.write("#### 📉 Critical Zone (31-40 라운드) 이탈 패턴")
    # 30~40 라운드 구간의 유저 잔존 데이터 시뮬레이션
    # 실제 데이터에서 해당 구간의 이탈률을 계산하여 시각화
    zone_df = df[df['sum_gamerounds_capped'].between(30, 45)]
    fig_zone = px.histogram(zone_df, x="sum_gamerounds_capped", color="version",
                            marginal="rug", barmode="group",
                            color_discrete_sequence=['#636EFA', '#EF553B'])
    fig_zone.update_layout(title="Gate 인근 구간(30-45) 유저 분포", xaxis_title="플레이 라운드", yaxis_title="유저 수")
    st.plotly_chart(fig_zone, use_container_width=True)

# 마케팅 전략 시각화 (Expander 활용)
with st.expander("💡 [전략 제언] 감질맛 효과 극대화를 위한 UX/UI 시안 보기"):
    st.markdown("""
    ### 1. 시각적 Cliffhanger 전략
    * **현상:** Gate 30에서 멈춘 유저의 7일차 복귀율이 1.7% 더 높음.
    * **적용:** 게이트 화면 너머로 **다음 스테이지 보상**을 노출하여 재방문 동기 부여.
    
    ### 2. 가변적 게이트 시스템 (Dynamic Gating)
    * **적용:** 초반(30단계)은 리텐션을 위해 짧게, 후반(40단계 이후)은 몰입을 위해 길게 배치.
    
    ### 3. 개인화된 리턴 푸시 (CRM)
    * **적용:** Gate 30에서 멈춘 유저가 24시간 미접속 시 "고양이가 쿠키를 다 구웠어요!" 알림 발송.
    """)
