import streamlit as st

st.set_page_config(page_title="Simple Resume Builder")

st.title("📄 Simple Resume Builder")

# Input fields
name = st.text_input("Full Name")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
summary = st.text_area("Professional Summary")

st.subheader("Skills")
skills = st.text_area("Enter skills separated by commas")

st.subheader("Experience")
experience = st.text_area("Enter work experience")

st.subheader("Education")
education = st.text_area("Enter education details")

# Generate resume
if st.button("Generate Resume"):
    resume_text = f"""
    -------------------------------
             RESUME
    -------------------------------
    Name: {name}
    Email: {email}
    Phone: {phone}

    Professional Summary:
    {summary}

    Skills:
    {skills}

    Experience:
    {experience}

    Education:
    {education}
    """
    st.success("Resume Generated Successfully!")
    st.text(resume_text)

    # Download resume
    st.download_button(
        label="📥 Download Resume",
        file_name="resume.txt",
        mime="text/plain",
        data=resume_text
    )
