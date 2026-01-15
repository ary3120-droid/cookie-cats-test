import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cookie Cats Test", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

df = load_data()

st.title("🎮 Cookie Cats A/B Test Dashboard")
st.success("데이터 연결 성공!")

# 간단한 지표 보여주기
col1, col2 = st.columns(2)
retention = df.groupby('version')['retention_7'].mean()
col1.metric("gate_30 리텐션", f"{retention['gate_30']:.2%}")
col2.metric("gate_40 리텐션", f"{retention['gate_40']:.2%}")

# 차트 하나 그리기
fig, ax = plt.subplots()
sns.barplot(x=retention.index, y=retention.values, ax=ax)
st.pyplot(fig)
