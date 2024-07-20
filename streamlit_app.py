import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
from groq import Groq

# Thiết lập API key của Groqcloud
api_key = "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"
client = Groq(api_key=api_key)

# Define the prompt for analyzing customer data
analysis_system_prompt = """
You are an AI assistant specialized in analyzing customer data to extract key issues, processes, and formulas.
Analyze the data and extrct relevant information:

### Extracted Information
- Issues: deduce what data constraints and key information are needed
- Formulas: Formulas that may be present in the data
"""

# Define the environmental prompt for 5W1H
environment_prompt = """
You are an AI assistant specialized in digital transformation solutions for software development (websites, apps, etc.). Use the 5W1H method to support analysis teams, saving time in surveying and implementing software functions. Follow these steps:

### Step by step analysis according to the following structure
1. **What**: Describe the problem or request the user has.
    - **How**:
        - Solution name:

2. **Why**: Explain why this problem occurred or needs to be solved.
    - **How**:
        - Solution name:

3. **Who**: Identify stakeholders (who are the users? what is their position and role in solving the problem)
    - **How**:
        - Solution name:

4. **When**: Solve problems for different times (maybe conditions to trigger a feature in the function)
    - **How**:
      - Solution name:

5. **Where**: Identify where the problem needs to be solved or created (for example, there are 10 steps, the problem is created in step 2 and affects step 5, each location needs to be clearly identified to solve)
    - **How**:
      - Solution name:

6. **How**: Synthesize and propose potential solutions based on the above content.
"""

suggestion_system_prompt = """
You are an expert AI assistant with 10 years of experience in Large Language Models (LLMs). Your role is to help users assist them in
describing software functions based on their input name and analyzed data. Follow these steps to provide detailed and accurate responses:

**Analyze the Text Data:**
   - Use advanced natural language processing techniques to extract key insights and relevant information from the provided text data.
   - Identify patterns, trends, and any notable data points that might influence the function's design.

**Generate Function Description:**
   - Based on the user's function name and the insights gained from the text analysis, draft a detailed description of the function.
   - Ensure the description includes:
     - Purpose of the function
     - Key features and capabilities
     - Potential use cases and benefits
     - Any prerequisites or required inputs for the function to operate effectively

### Example Format:
Based on the text data, here's a draft description for the "User Engagement Tracker" function:
- **Purpose:** Track and analyze user engagement metrics across various platforms.
- **Key Features:** Real-time tracking, detailed analytics dashboard, customizable reports, and trend prediction.
- **Use Cases:** Monitor user activity, identify high engagement periods, optimize content strategy, and improve user retention.
- **Prerequisites:** Requires access to user activity data and integration with analytics tools.
"""


# Streamlit interface
st.title("Digital Transformation Solutions Assistant")
st.write("Use the 5W1H method to analyze and generate solutions for software functions.")

# File upload
st.subheader("Upload supporting documents:")
uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "xls", "pdf", "png", "jpg", "jpeg"])

def extract_from_excel(file):
    df = pd.read_excel(file)
    return df

def extract_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

if uploaded_file:
    if uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        data = extract_from_excel(uploaded_file).to_string()
    elif uploaded_file.type == "application/pdf":
        data = extract_from_pdf(uploaded_file)
    elif uploaded_file.type in ["image/png", "image/jpeg"]:
        data = extract_from_image(uploaded_file)

    # st.write("Extracted Data:")
    # st.write(data)
    st.write("Data has been extracted!")

    if st.button("Analyze the extracted data"):
        # Analyze the extracted data
        analysis_prompt = "Please analysis this data:\n" + data

        analysis_data = {
            "model": "llama3-groq-70b-8192-tool-use-preview",
            "messages": [
                {"role": "system", "content": analysis_system_prompt},
                {"role": "user", "content": analysis_prompt}]
        }
        analysis_completion = client.chat.completions.create(**analysis_data)
        analysis_response = analysis_completion.choices[0].message.content

        st.session_state.analysis_response = analysis_response
        st.write("Analysis Result:")
        st.write(analysis_response)

if 'analysis_response' in st.session_state:
    st.subheader("Select a Function for Detailed Description")
    selected_function = st.text_input("Enter the function you want to learn more about:")

    if st.button("Get Function Description"):
        function_prompt = f"""
        Analyzed Data:
        {st.session_state.analysis_response}
        Function Name: {selected_function}
        """

        function_data = {
            "model": "llama3-groq-70b-8192-tool-use-preview",
            "messages": [
                {"role": "system", "content": suggestion_system_prompt},
                {"role": "user", "content": function_prompt}]
        }
        function_completion = client.chat.completions.create(**function_data)
        function_response = function_completion.choices[0].message.content
        st.write("Function Description:")
        st.write(function_response)
