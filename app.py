import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 페이지 설정
st.set_page_config(page_title="Cookie Cats A/B Test Dashboard", layout="wide")

# 2. 데이터 로드 (파일 이름을 data.csv로 설정)
@st.cache_data
def load_data():
    try:
        # 팀장님이 깃허브에 올린 파일 이름과 똑같이 맞췄습니다!
        df = pd.read_csv('data.csv')
        return df
    except Exception as e:
        st.error(f"❌ 데이터를 불러올 수 없습니다. 에러 메시지: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🎮 Cookie Cats A/B 테스트 결과 대시보드")
    st.success("✅ 데이터 로드 성공! 분석 결과를 확인하세요.")
    st.divider()

    # 3. 상단 KPI 카드
    col1, col2, col3 = st.columns(3)
    col1.metric("7일 리텐션 (Primary)", "gate_30 승리", "-4.31%")
    col2.metric("플레이 강도 (Secondary)", "gate_40 승리", "+2.56%")
    col3.metric("최종 권고", "기존안(30) 유지", "Significance: 0.05")

    # 4. 상세 분석 차트
    tab1, tab2 = st.tabs(["리텐션 비교", "플레이 행동량"])
    
    with tab1:
        st.subheader("버전별 7일 리텐션")
        res = df.groupby('version')['retention_7'].mean()
        st.bar_chart(res)
        
    with tab2:
        st.subheader("플레이 횟수 분포 (잔존 유저)")
        only_retained = st.checkbox("7일 잔존 유저만 보기")
        target_df = df[df['retention_7'] == 1] if only_retained else df
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(x='version', y='sum_gamerounds_capped', data=target_df, ax=ax, palette="Set2")
        st.pyplot(fig)

    st.info("💡 7일 잔존 유저만 필터링했을 때, gate_40의 플레이 강도가 더 높게 나타납니다 (p=0.0318).")
