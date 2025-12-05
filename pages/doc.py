import streamlit as st
import boto3
import json

# -----------------------------
# CONFIG
# -----------------------------
AWS_REGION = "ap-south-1"
BUCKET = "career-copilot-docsverification"      # CHANGE THIS
USER_ID = "user1"

s3 = boto3.client("s3", region_name=AWS_REGION)
textract = boto3.client("textract", region_name=AWS_REGION)

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION
)

# -----------------------------
# S3 Upload
# -----------------------------
def upload_to_s3(file, key):
    s3.upload_fileobj(file, BUCKET, key)
    return f"s3://{BUCKET}/{key}"


# -----------------------------
# Textract - FORMS Extraction
# -----------------------------
def extract_textract_forms(file_key):
    response = textract.analyze_document(
        Document={"S3Object": {"Bucket": BUCKET, "Name": file_key}},
        FeatureTypes=["FORMS"]
    )
    return response


# -----------------------------
# Textract - ONLY TEXT (for Resume)
# -----------------------------
def extract_text_from_resume(file_key):
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': BUCKET, 'Name': file_key}}
    )

    full_text = ""
    for b in response["Blocks"]:
        if b["BlockType"] == "LINE":
            full_text += b["Text"] + "\n"

    return full_text


# -----------------------------
# Save JSON to S3
# -----------------------------
def save_json_s3(data, key):
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data)
    )


# -----------------------------
# Parse Textract Key-Value pairs
# -----------------------------
def parse_textract_kv(textract_json):
    blocks = textract_json["Blocks"]
    kv = {}

    for block in blocks:
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            
            key_text = ""
            value_text = ""

            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for id_ in rel["Ids"]:
                        child = next(b for b in blocks if b["Id"] == id_)
                        key_text += child.get("Text", "") + " "

                if rel["Type"] == "VALUE":
                    for id_ in rel["Ids"]:
                        child = next(b for b in blocks if b["Id"] == id_)
                        value_text += child.get("Text", "") + " "

            kv[key_text.strip()] = value_text.strip()

    return kv


# -----------------------------
# Bedrock - Resume JSON Generator
# -----------------------------
def bedrock_resume_json(text):

    prompt = f"""
    You are an expert resume parser.
    Convert the following resume into structured JSON:

    {{
        "name": "",
        "email": "",
        "phone": "",
        "education": [
            {{"degree": "", "college": "", "year": "", "cgpa": ""}}
        ],
        "skills": [],
        "projects": []
    }}

    Resume text:
    {text}
    """

    response = bedrock.invoke_model(
        modelId="amazon.titan-text-lite-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": prompt})
    )

    out = json.loads(response["body"].read())
    return json.loads(out["results"][0]["outputText"])


# -----------------------------
# Compare Resume vs Document
# -----------------------------
def compare_data(resume, docs):

    issues = []

    # Name Check
    if resume["name"].lower() != docs.get("Name", "").lower():
        issues.append("Name mismatch")

    # Year Check
    if "year" in resume["education"][0]:
        if resume["education"][0]["year"] != docs.get("Year of Passing", ""):
            issues.append("Year of Passing mismatch")

    # CGPA Check
    if "cgpa" in resume["education"][0]:
        if resume["education"][0]["cgpa"] != docs.get("CGPA", ""):
            issues.append("CGPA mismatch")

    return issues


# -----------------------------
# Bedrock - Final Verification Report
# -----------------------------
def generate_verification_report(resume, docs, issues):

    prompt = f"""
    You are a document verification system.

    Resume Data: {resume}
    Document Data: {docs}
    Mismatches Found: {issues}

    Create a clear verification report.
    Include:
    - Summary
    - List of issues
    - Fraud probability (High/Medium/Low)
    - Credibility score (0-100)

    Respond in JSON:
    {{
        "summary": "",
        "issues": [],
        "fraud_probability": "",
        "credibility_score": 0
    }}
    """

    response = bedrock.invoke_model(
        modelId="amazon.titan-text-lite-v1",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": prompt})
    )

    output = json.loads(response["body"].read())
    return json.loads(output["results"][0]["outputText"])


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("📄 Full Module-4: Document + Resume Verification")


resume_file = st.file_uploader("Upload Resume (PDF)")
doc_file = st.file_uploader("Upload Marksheet / Degree Certificate")


if resume_file and doc_file:

    st.success("Files received!")

    # --------------------------
    # 1) Upload both files
    # --------------------------
    resume_key = f"users/{USER_ID}/resume.pdf"
    doc_key = f"users/{USER_ID}/{doc_file.name}"

    upload_to_s3(resume_file, resume_key)
    upload_to_s3(doc_file, doc_key)

    st.info("Files uploaded to S3")

    # --------------------------
    # 2) Textract document extraction
    # --------------------------
    doc_raw = extract_textract_forms(doc_key)
    doc_clean = parse_textract_kv(doc_raw)

    save_json_s3(doc_raw, f"textract_raw/{USER_ID}/doc_raw.json")
    save_json_s3(doc_clean, f"textract_clean/{USER_ID}/doc_clean.json")

    st.subheader("📌 Extracted Document Data:")
    st.json(doc_clean)

    # --------------------------
    # 3) Resume text extraction
    # --------------------------
    resume_text = extract_text_from_resume(resume_key)

    # --------------------------
    # 4) Resume JSON (via Bedrock)
    # --------------------------
    resume_json = bedrock_resume_json(resume_text)

    save_json_s3(resume_json, f"textract_clean/{USER_ID}/resume_clean.json")

    st.subheader("📌 Extracted Resume JSON:")
    st.json(resume_json)

    # --------------------------
    # 5) Compare Resume vs Document
    # --------------------------
    issues = compare_data(resume_json, doc_clean)

    st.subheader("⚠ Mismatches Found:")
    st.write(issues if issues else "No issues found!")

    # --------------------------
    # 6) Final Verification Report (Bedrock)
    # --------------------------
    report = generate_verification_report(resume_json, doc_clean, issues)

    st.subheader("📝 Final Verification Report:")
    st.json(report)

    # --------------------------
    # 7) Save Report to S3
    # --------------------------
    save_json_s3(report, f"reports/{USER_ID}/final_report.json")

    st.success("Verification completed! Report saved in S3.")