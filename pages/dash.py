import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="🖥️", layout="wide")

# Authentication check
if "authenticated" not in st.session_state or st.session_state["authenticated"] is not True:
    st.warning("⚠️ Please login first")
    st.stop()

st.title("🚀 Career Copilot Dashboard")
st.subheader("Choose a Service")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("🧠 Question Generator")
    st.write("Generate Company + Role based interview questions.")
    if st.button("Open Question Generator"):
        st.switch_page("pages/comp_ques.py")

with col2:
    st.header("📄 Resume Builder")
    st.write("Build and format a professional resume.")
    if st.button("Open Resume Builder"):
        st.switch_page("pages/res.py")

with col3:
    st.header("🔍 Document Verification")
    st.write("Upload & verify documents for authenticity.")
    if st.button("Open Document Verification"):
        st.switch_page("pages/doc.py")
