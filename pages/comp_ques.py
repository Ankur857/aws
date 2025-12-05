import streamlit as st
import requests

st.set_page_config(page_title="Interview Question Generator", page_icon="🎯")

st.title("🎓 Career Copilot - Interview Question Generator")

# API URL
API_URL = "https://4psklumjfd.execute-api.ap-south-1.amazonaws.com/prod/interview"

# Dropdowns
company = st.selectbox("Select Company", ["Google", "Amazon", "Microsoft"])
role = st.selectbox("Select Role", ["SDE", "ML Engineer", "Data Scientist"])

# Generate Button
if st.button("🎯 Generate Interview Questions"):
    st.info("⏳ Generating questions... Please wait...")

    payload = {"company": company, "role": role}

    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                st.success("✅ Success! Questions generated below:")
                
                st.write(f"### 🏢 Company: **{data.get('company')}**")
                st.write(f"### 👨‍💻 Role: **{data.get('role')}**")
                st.markdown("---")
                st.write(data.get("content"))
            else:
                st.error(f"❌ Error: {data.get('error')}")
        else:
            st.error(f"❌ API Response Error: {response.status_code}")

    except Exception as e:
        st.error(f"❌ Network Error: {e}")
