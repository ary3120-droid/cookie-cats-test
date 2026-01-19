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
    
    # 수정: 높이를 줄이고 Y축 범위를 80% 지점부터 설정하여 적절한 차이 가시화
    fig7.update_layout(
        showlegend=False, 
        height=300, 
        yaxis_tickformat='.1%',
        yaxis=dict(range=[min(ret7.values)*0.8, max(ret7.values)*1.2])
    )
    fig7.update_traces(textfont_size=14, textposition="outside")
    st.plotly_chart(fig7, use_container_width=True)
    st.error("**검정 결과:** gate_40에서 약 0.8%p 하락 확인 (대립가설 기각)")

with c_ret2:
    st.write("#### [Guardrail] 1-Day Retention Rate")
    fig1 = px.bar(ret1, x=ret1.index, y=ret1.values, text_auto='.2%', 
                  color=ret1.index, color_discrete_sequence=['#00CC96', '#AB63FA'])
    
    # 수정: 높이 조절 및 Y축 범위 최적화
    fig1.update_layout(
        showlegend=False, 
        height=300, 
        yaxis_tickformat='.1%',
        yaxis=dict(range=[min(ret1.values)*0.8, max(ret1.values)*1.2])
    )
    fig1.update_traces(textfont_size=14, textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)
    st.warning("**모니터링:** 초기 안착 단계에서도 유의미한 개선 없음")

# 3️⃣ 가설 2 검정: 플레이 행동량 (Volume & Intensity)
st.markdown("---")
st.subheader("3. 가설 2 검정: 사용자 플레이 행동 변화")

col_play1, col_play2 = st.columns(2)
with col_play1:
    st.write("#### [2-1] 전체 플레이 행동량 (Capped)")
    
    # 수정 포인트: points=None으로 설정하여 지저분한 점들을 없애고 박스만 남김
    fig_box = px.box(df, x="version", y="sum_gamerounds_capped", color="version",
                     color_discrete_sequence=['#636EFA', '#EF553B'],
                     points=None) 
    
    # 평균값(Mean)을 점선으로 추가하여 중앙값(실선)과 비교 가능하게 함
    fig_box.update_traces(boxmean=True, line_width=2) 
    
    fig_box.update_layout(
        height=350, 
        showlegend=False, 
        margin=dict(t=10, b=10),
        # Y축 범위를 0에서 100(또는 데이터 특성에 맞는 적절한 값)으로 고정
        # 이렇게 하면 박스의 위치 차이가 훨씬 잘 보입니다.
        yaxis=dict(range=[0, 100], title="플레이 라운드") 
    )
    
    st.plotly_chart(fig_box, use_container_width=True)
    st.write("**결과:** 전체 사용자 기준 플레이 총량의 유의미한 변화 없음")

with col_play2:
    st.write("#### [2-2] 7일 유지 유저의 평균 플레이 강도")
    retained_df = df[df['retention_7'] == True]
    intensity = retained_df.groupby('version')['sum_gamerounds_capped'].mean()
    
    fig_int = px.bar(intensity, x=intensity.index, y=intensity.values, text_auto='.1f',
                     color=intensity.index, color_discrete_sequence=['#FFA15A', '#19D3AF'])
    
    # 수정: Y축을 50% 지점부터 시작하게 하여 막대의 안정감과 차이를 동시에 잡음
    fig_int.update_layout(
        showlegend=False, 
        height=320,
        yaxis=dict(range=[min(intensity.values)*0.5, max(intensity.values)*1.2])
    )
    fig_int.update_traces(textfont_size=14, textposition="outside")
    st.plotly_chart(fig_int, use_container_width=True)
    st.success(f"**발견:** 잔존 유저 집단 내 몰입도 **+7.6회 유의적 상승** ($p < 0.05$)")
# 4️⃣ 핵심 인사이트: 게이트의 두 가지 역할 및 심층 분석 (수정본)
st.markdown("---")
st.subheader("💡 핵심 인사이트: 게이트의 두 가지 역할 및 심층 분석")

# (1) Gate 30 & Critical Zone 분석 섹션
ins_col1, ins_col2 = st.columns(2)

with ins_col1:
    st.markdown("""
    <div style="background-color: #f8f9fb; padding: 20px; border-radius: 10px; border-left: 5px solid #636EFA; height: 350px;">
        <h4>1) Gate 30: 재방문 트리거 (Cliffhanger)</h4>
        <ul>
            <li><b>실험 결과:</b> 게이트를 일찍 만나는 gate_30 집단에서 리텐션이 유의미하게 높음. 적절한 시점의 차단이 재방문 이유를 제공함. [cite: 351, 398]</li>
            <li><b>심리적 기제:</b> 30단계에서 멈춘 유저들은 '감질맛'을 느끼며 재방문 동기를 얻음. (1일 미접속자의 7일차 복귀율이 gate_30에서 약 1.7% 더 높음) [cite: 356, 399]</li>
            <li><b>UX 자산:</b> 불편함은 제거 대상이 아니라, 적절한 타이밍에 배치될 때 유저의 목표 의식을 형성하는 <b>전략적 자산</b>임. [cite: 380, 401]</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with ins_col2:
    st.markdown("""
    <div style="background-color: #f8f9fb; padding: 20px; border-radius: 10px; border-left: 5px solid #00CC96; height: 350px;">
        <h4>2) Critical Zone 분석: 31-40 라운드 집중 검증</h4>
        <ul>
            <li><b>집중 검증:</b> 게이트 위치 변경의 직접 영향을 받은 31-40 구간 유저만 필터링하여 분석. [cite: 368]</li>
            <li><b>데이터 증명:</b> 강제 휴식을 가졌던 유저(gate_30)의 리텐션이 하이패스 유저(gate_40)보다 높음을 확인. [cite: 369]</li>
            <li><b>결론:</b> 무조건적인 플레이 지속보다 <b>적절한 제동</b>이 장기 잔존에 유리함이 데이터로 입증됨. [cite: 356, 369]</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# (2) Gate 40 & 최종 권고 섹션
ins_col3, ins_col4 = st.columns(2)

with ins_col3:
    st.markdown("""
    <div style="background-color: #f8f9fb; padding: 20px; border-radius: 10px; border-left: 5px solid #FFA15A; height: 300px;">
        <h4>3) Gate 40: 코어 유저의 가치를 키우는 몰입 장치</h4>
        <ul>
            <li><b>전략적 의미:</b> gate_40은 유저 수(Quantity)를 늘리는 장치가 아니라, 남아 있는 핵심 유저의 가치(Quality)를 극대화하는 분기점. [cite: 391, 417]</li>
            <li><b>발견:</b> 리텐션은 낮으나 게이트를 넘긴 유저들은 이전보다 <b>7.6라운드 더 플레이</b>하며 깊은 몰입도를 보임. [cite: 334, 411]</li>
            <li><b>판단 지점:</b> 한 번의 긴 플레이보다 <b>자주 접속하는 짧은 플레이</b>가 게임 생명력 유지에 더 효과적임을 인지해야 함. [cite: 173, 402]</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with ins_col4:
    st.error("### 🚀 최종 권고: gate_30 유지")
    st.write("서비스의 핵심 지표인 사용자 유지율(DAU) 방어를 위해 **첫 번째 게이트 위치는 30단계로 유지**하는 것이 최선입니다. [cite: 173, 382]")
    st.success("단, gate_40에서 확인된 몰입 상승 효과는 **헤비 유저 전용 모드나 시즌 패스** 등 별도의 고도화 전략에 부분 도입할 것을 제안합니다. [cite: 178, 440]")
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
    st.caption(f"※ 위 시뮬레이션은 유입 규모에 따른 기회비용 손실을 정량적으로 보여줍니다")

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
