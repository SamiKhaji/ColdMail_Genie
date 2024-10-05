import streamlit as st
from langchain.document_loaders import WebBaseLoader  # Ensure this import is correct
from chains import Chain
from portfolio import Portfolio
from utils import clean_text



def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 ColdMail Genie")
    url_input = st.text_input("Enter a job posting link:", placeholder="https:careers/jobs.ABC.com/job/R-1235")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            page_content = loader.load()

            if not page_content:
                st.error("No data retrieved from the URL. Please check the link.")
                return

            cleaned_data = clean_text(page_content.pop().page_content)
            if not cleaned_data:
                st.error("Cleaned data is empty. Please check the URL.")
                return

            portfolio.load_portfolio()
            jobs = llm.extract_jobs(cleaned_data)

            seen_jobs = set()  # To track processed job descriptions
            for job in jobs:
                # Check if necessary job details are available
                if job.get('role') == "Not specified" or job.get('skills') == "Not specified":
                    continue  # Skip this job if essential details are missing

                job_description = str(job)  # Convert job to string for uniqueness check
                if job_description not in seen_jobs:
                    seen_jobs.add(job_description)  # Mark this job as seen
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills)

                    # Generate the email
                    email = llm.write_mail(job, links)

                    # Display the generated email
                    st.subheader(f"Email for {job.get('role')}:")
                    st.code(email, language='markdown')  # Display email in code block

        except Exception as e:
            st.error(f"An Error Occurred: {e}")
            print("Debug Info:", e)


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="ColdMail Genie", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
