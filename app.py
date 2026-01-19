import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 및 데이터 로드 (최상단 고정)
st.set_page_config(page_title="Cookie Cats A/B Test Analysis", layout="wide")

@st.cache_data
def load_data():
    # 데이터 파일명이 깃허브의 파일명과 동일해야 합니다.
    df = pd.read_csv('data.csv')
    df['retention_1'] = df['retention_1'].astype(bool)
    df['retention_7'] = df['retention_7'].astype(bool)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 커스텀 CSS
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

st.info("💡 **SRM 확인:** 미세한 샘플 불균형이 관측되나, 대규모 표본에 따른 통계적 민감성으로 판단됨.")

# 2️⃣ 가설 1 검정: 리텐션
st.markdown("---")
st.subheader("2. 가설 1 검정: 사용자 리텐션 영향 분석")
ret7 = df.groupby('version')['retention_7'].mean()
ret1 = df.groupby('version')['retention_1'].mean()

c_ret1, c_ret2 = st.columns(2)
with c_ret1:
    st.write("#### [Primary] 7-Day Retention Rate")
    fig7 = px.bar(ret7, x=ret7.index, y=ret7.values, text_auto='.2%', 
                  color=ret7.index, color_discrete_sequence=['#636EFA', '#EF553B'])
    fig7.update_layout(showlegend=False, height=300, yaxis_tickformat='.1%',
                        yaxis=dict(range=[min(ret7.values)*0.8, max(ret7.values)*1.2]))
    fig7.update_traces(textfont_size=14, textposition="outside")
    st.plotly_chart(fig7, use_container_width=True)
    st.error("**검정 결과:** gate_40에서 약 0.8%p 하락 확인 (기존안 30 우위)")

with c_ret2:
    st.write("#### [Guardrail] 1-Day Retention Rate")
    fig1 = px.bar(ret1, x=ret1.index, y=ret1.values, text_auto='.2%', 
                  color=ret1.index, color_discrete_sequence=['#00CC96', '#AB63FA'])
    fig1.update_layout(showlegend=False, height=300, yaxis_tickformat='.1%',
                        yaxis=dict(range=[min(ret1.values)*0.8, max(ret1.values)*1.2]))
    fig1.update_traces(textfont_size=14, textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)
    st.warning("**모니터링:** 초기 안착 단계에서도 유의미한 개선 없음")

# 3️⃣ 가설 2 검정: 플레이 행동량
st.markdown("---")
st.subheader("3. 가설 2 검정: 사용자 플레이 행동 변화")
col_play1, col_play2 = st.columns(2)
with col_play1:
    st.write("#### [2-1] 전체 플레이 행동량 (Capped)")
    fig_box = px.box(df, x="version", y="sum_gamerounds_capped", color="version",
                     color_discrete_sequence=['#636EFA', '#EF553B'], points=None) 
    fig_box.update_traces(boxmean=True, line_width=2) 
    fig_box.update_layout(height=350, showlegend=False, yaxis=dict(range=[0, 100], title="플레이 라운드"))
    st.plotly_chart(fig_box, use_container_width=True)
    st.write("**결과:** 전체 사용자 기준 플레이 총량의 유의미한 변화 없음")

with col_play2:
    st.write("#### [2-2] 7일 유지 유저의 평균 플레이 강도")
    intensity = df[df['retention_7'] == True].groupby('version')['sum_gamerounds_capped'].mean()
    fig_int = px.bar(intensity, x=intensity.index, y=intensity.values, text_auto='.1f',
                     color=intensity.index, color_discrete_sequence=['#FFA15A', '#19D3AF'])
    fig_int.update_layout(showlegend=False, height=320, yaxis=dict(range=[min(intensity.values)*0.5, max(intensity.values)*1.2]))
    fig_int.update_traces(textfont_size=14, textposition="outside")
    st.plotly_chart(fig_int, use_container_width=True)
    st.success(f"**발견:** 잔존 유저 집단 내 몰입도 **+7.6회 유의적 상승**")

# 4️⃣ 핵심 인사이트 및 비즈니스 제언
st.markdown("---")
st.subheader("💡 핵심 인사이트 및 비즈니스 제언")
col_ins1, col_ins2 = st.columns(2)
with col_ins1:
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 100%;">
        <h4>✅ 왜 Gate 30인가? (Retention)</h4>
        <ul>
            <li><b>감질맛 효과:</b> 이른 차단이 유저에게 '미완성 과업' 인식을 주어 재방문 유도</li>
            <li><b>적절한 제동:</b> 무조건적인 플레이보다 <b>강제 휴식</b>이 장기 잔존에 유리함 증명</li>
            <li><b>결과:</b> 7일 리텐션 지표에서 <b>Gate 30이 압도적 우위</b></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with col_ins2:
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 100%;">
        <h4>🚀 Gate 40의 활용 (Engagement)</h4>
        <ul>
            <li><b>코어 유저 몰입:</b> 잔존 유저의 인당 플레이 횟수 <b>+7.6회 상승</b> 확인</li>
            <li><b>선별 효과:</b> 유저 수는 줄지만, 남은 유저의 <b>질적 가치(LTV)</b>는 높아짐</li>
            <li><b>제언:</b> 헤비 유저 전용 콘텐츠나 <b>수익화 모델(BM)</b> 설계에 활용 권장</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
st.warning("⚠️ **최종 판단:** 리텐션 방어가 최우선이므로 **기존안(Gate 30) 유지를 권고**합니다.")

# 5️⃣ 전략 제언 섹션
st.markdown("---")
st.subheader("🚀 데이터 기반 전략 제언 (Strategy Roadmap)")
str_col1, str_col2, str_col3 = st.columns(3)
with str_col1:
    st.markdown("""
    <div style="background-color: #f8f9fb; padding: 15px; border-radius: 10px; border-top: 5px solid #636EFA; height: 100%;">
        <h4>1. 서비스 기획</h4>
        <p><b>감질맛 효과(Cliffhanger)의 극대화</b></p>
        <ul>
            <li><b>시각적 동기부여:</b> 차단 화면 너머로 다음 보상이나 애니메이션을 노출하여 다음 단계에 대한 기대감 형성</li>
            <li><b>하이브리드 게이트 설계:</b> 리텐션이 중요한 초반부(30단계)는 짧게, 몰입도가 검증된 후반부는 간격을 넓히는 가변적 설계 제안</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with str_col2:
    st.markdown("""
    <div style="background-color: #f8f9fb; padding: 15px; border-radius: 10px; border-top: 5px solid #00CC96; height: 100%;">
        <h4>2. 마케팅 (CRM)</h4>
        <p><b>데이터 기반 맞춤형 복귀 알림</b></p>
        <ul>
            <li><b>타겟팅 알림:</b> 30단계 근처 정체 유저 대상 "고양이가 당신을 기다리고 있어요"와 같은 감성적 푸시 알림 발송</li>
            <li><b>복귀 유도 리워드:</b> 이탈 유저 복귀 시 게이트 즉시 통과 열쇠나 단발성 아이템을 지급하여 재진입 장벽 완화</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
with str_col3:
    st.markdown("""
    <div style="background-color: #f8f9fb; padding: 15px; border-radius: 10px; border-top: #FFA15A 5px solid; height: 100%;">
        <h4>3. 사업 및 BM 전략</h4>
        <p><b>코어 유저 타겟팅 강화</b></p>
        <ul>
            <li><b>찐팬 전용 패키지:</b> 몰입도가 검증된 Gate 40 통과 유저군에게만 노출되는 기간 한정 고효율 패키지로 전환율 극대화</li>
            <li><b>연속성 유지 상품:</b> 플레이 강도가 높아진 유저를 위한 하트 회복 속도 향상 월정액 등 게임 생명력과 수익성 동시 확보</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
st.caption("※ 위 전략은 실험에서 도출된 리텐션(Gate 30)과 몰입도(Gate 40)의 상충 관계를 비즈니스 가치로 전환하기 위한 로드맵입니다.")

# 6️⃣ 비즈니스 임팩트 분석
st.markdown("---")
st.subheader("💰 비즈니스 임팩트 시뮬레이션")
col_biz1, col_biz2 = st.columns(2)
with col_biz1:
    ret_diff = 0.0082 
    new_users = st.number_input("월간 신규 유입 유저(UA) 설정", value=100000, step=10000)
    lost = int(new_users * ret_diff)
    st.error(f"**월간 예상 잔존 유저 손실: 약 {lost:,}명**")
with col_biz2:
    zone_df = df[df['sum_gamerounds_capped'].between(30, 45)]
    fig_zone = px.histogram(zone_df, x="sum_gamerounds_capped", color="version", barmode="group",
                            color_discrete_sequence=['#636EFA', '#EF553B'])
    fig_zone.update_layout(title="Gate 인근 구간(30-45) 유저 분포", xaxis_title="플레이 라운드", yaxis_title="유저 수")
    st.plotly_chart(fig_zone, use_container_width=True)
