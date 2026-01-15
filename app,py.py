import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="Cookie Cats A/B Test Dashboard", layout="wide")

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cookie_cats_for_tableau.csv')
        return df
    except FileNotFoundError:
        st.error("❌ 'cookie_cats_for_tableau.csv' 파일을 찾을 수 없습니다. 같은 폴더에 있는지 확인해주세요!")
        return None

df = load_data()

if df is not None:
    # 사이드바
    st.sidebar.title("📊 분석 메뉴")
    page = st.sidebar.radio("보고 싶은 화면", ["실험 요약(Summary)", "데이터 상세 분석"])

    # 화면 1: 실험 요약
    if page == "실험 요약(Summary)":
        st.title("🎮 Cookie Cats 게이트 위치 변경 A/B 테스트")
        st.markdown("---")
        
        # KPI 지표 카드
        col1, col2, col3 = st.columns(3)
        col1.metric("7일 리텐션 (Primary)", "gate_30 승리", "-4.31% 하락")
        col2.metric("플레이 강도 (Secondary)", "gate_40 승리", "+2.56% 상승")
        col3.metric("최종 권고안", "기존안(30) 유지", "Significance: 0.05")

        st.subheader("💡 분석가 인사이트")
        st.warning("""
        **종합 판정:**
        - 게이트를 40레벨로 미룰 경우, 전체 사용자의 **7일 리텐션이 4.3% 하락**하는 치명적인 결과가 확인되었습니다.
        - 비록 이탈하지 않은 충성 고객의 플레이 횟수는 2.5% 상승(p=0.03)했으나, 전체 유저 파이를 유지하는 것이 우선입니다.
        - 따라서 **현재의 30레벨 게이트 배치를 유지**할 것을 강력히 권고합니다.
        """)

    # 화면 2: 데이터 상세 분석
    else:
        st.title("📈 상세 데이터 시각화")
        
        # 탭 구성
        tab1, tab2 = st.tabs(["리텐션 비교", "플레이 행동량 분포"])
        
        with tab1:
            st.subheader("버전별 리텐션 평균")
            metric = st.selectbox("지표 선택", ["retention_7", "retention_1"])
            res = df.groupby('version')[metric].mean()
            st.bar_chart(res)
            st.write(f"각 버전의 {metric} 평균 비율입니다. gate_30이 더 높은 것을 확인할 수 있습니다.")

        with tab2:
            st.subheader("플레이 횟수 분포 (Box Plot)")
            only_retained = st.checkbox("7일 잔존 유저만 보기 (Play Intensity 분석)")
            
            target_df = df[df['retention_7'] == 1] if only_retained else df
            
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.boxplot(x='version', y='sum_gamerounds_capped', data=target_df, ax=ax, palette="Set2")
            plt.title("Gamerounds Distribution")
            st.pyplot(fig)
            
            if only_retained:
                st.write("✅ 7일 잔존 유저 집단에서는 gate_40의 분포가 미세하게 높음이 관찰됩니다 (p=0.0318).")