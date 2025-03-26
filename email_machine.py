from demo import PiiDetection
import streamlit as st
import pandas as pd

def main():
    #Page setting
    st.set_page_config(page_title="Review Email Content",
                       layout='centered',
                       initial_sidebar_state='collapsed', page_icon="🕵️")
    st.header("🕵️ PII Detector")

    # Email content input
    email_content = st.text_area('Enter the email content', height=200)

    #CSV
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to analyze for PII"
    )
    # CSV file preview
    csv_text = ""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, delimiter=";")
            st.write(f"CSV Overview:")
            st.write(f"Rows:{len(df)}")
            st.write(f"Columns: {', '.join(df.columns)}")
            st.write(df)
            csv_text = df.dropna().astype(str)
        except Exception as process_csv_error:
            raise process_csv_error

    review_style = st.selectbox( 'Styles:',
                                ('Quick Check', 'Detailed Check'),
                                index=0)
    analyze_button = st.button("Analyze")

    if analyze_button:
        # Combined results storage
        combined_results = {
            'email_results': [],
            'csv_results': []
        }

        # Validate input source(email, csv)
        if email_content.strip() is None and uploaded_file is None :
            st.warning("Please enter email content or upload a CSV file.")
            return

        is_detail = True if review_style == "Detailed Check" else False
        try:

            if email_content.strip():
                agent = PiiDetection(user_text=email_content,
                                     is_detail=is_detail)
                email_result = agent.detect_pii()
                combined_results["email_results"] = email_result
            if uploaded_file is not None:
                agent = PiiDetection(user_text=csv_text,
                                     is_detail=is_detail)

                csv_result = agent.detect_pii()
                combined_results["csv_results"] =csv_result

            # Results Display Section
            st.header("📊 PII Detection Results")
            if combined_results["email_results"]:
                st.subheader("📧 Email Content Analysis")
                st.write(combined_results["email_results"])
            if combined_results["csv_results"]:
                st.subheader("📄 CSV File Analysis")
                st.write(combined_results["csv_results"])
        except Exception as pii_agent_err:
            raise pii_agent_err


if __name__ == '__main__':
    main()
