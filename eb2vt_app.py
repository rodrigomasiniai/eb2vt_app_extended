import glob
import os
import urllib.request

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_tree_select import tree_select
import components.authenticate as authenticate


st.set_page_config(
    layout='wide',
    page_title="eb2vt",
    page_icon="🇺🇸"
    )

st.markdown('''<style>.css-1egvi7u {margin-top: -4rem;}</style>''',
    unsafe_allow_html=True)
# Design change spinner color to primary color
st.markdown('''<style>.stSpinner > div > div {border-top-color: #9d03fc;}</style>''',
    unsafe_allow_html=True)
# Design change min height of text input box
st.markdown('''<style>.css-15tx938{min-height: 0.0rem;}</style>''',
    unsafe_allow_html=True)
# Design hide top header line
hide_decoration_bar_style = '''<style>header {visibility: hidden;}</style>'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)
# Design hide "made with streamlit" footer menu area
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

md_files = sorted(
    [int(x.strip("Step").strip(".md")) for x in glob.glob1("content", "*.md")]
)

# Sidebar
st.sidebar.image(Image.open("bg1.png"))
st.sidebar.header("Tabs")
tabs = ["EB2-NIW Application Process Tutorial", "Checklist", "EB2Visaticket assistant"]
selected_tab = st.sidebar.radio("Select a tab", tabs)

st.sidebar.header("About")
st.sidebar.markdown(
    "[eb2visatickets](https://eb2visatickets.com) provides a reliable Tutorial for skilled immigrations who want to apply for EB2-NIW visa."
)

st.sidebar.header("Resources")
st.sidebar.markdown(
    """
- [USCIS](https://www.uscis.gov/)
- [Explore your options](https://www.uscis.gov/forms/explore-my-options)
- [Immigrant supporting](https://www.informedimmigrant.com/)
- [Statistics](https://www.dhs.gov/immigration-statistics)
"""
)

st.sidebar.header("Partners")
st.sidebar.markdown(
    "For technical guidance look for our [partner](https://progresspath.us)."
)
# Check authentication
authenticate.initialise_st_state_vars()

# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.logout_button()
else:
    authenticate.login_form()

# Rest of the page
st.sidebar.header("Thanks for buying your visa ticket!")

if (
    st.session_state["authenticated"]
):

    if selected_tab == "EB2-NIW Application Process Tutorial":
        # Logo and Navigation
        col1, col2, col3 = st.columns((1, 4, 1))
        with col1:
            st.markdown('''<style>.css-1egvi7u {margin-top: -4rem;}</style>''', unsafe_allow_html=True)
            st.markdown('')

        with col2: 
            st.markdown("""
            <div style="display:flex; justify-content:center;">
                <h1>🇺🇸 EB2-NIW Application Process Tutorial</h1>
            </div>
            """, unsafe_allow_html=True)
            
    
        steps_list = [f"Step {x}" for x in md_files]


        st.write("#### ⭐ Start your journey")

        selected_step = st.selectbox(
            "Select your Step:", steps_list
        )

            
            
        # Display content
        for i in steps_list:
            if selected_step == i:
                j = i.replace(" ", " ")
                with open(f"content/{j}.md", "r") as f:
                    st.markdown(f.read())
                if os.path.isfile(f"content/figures/{j}.csv") == True:
                    st.markdown("---")
                    st.markdown("### Figures")
                    df = pd.read_csv(f"content/figures/{j}.csv", engine="python")
                    for i in range(len(df)):
                        st.image(f"content/images/{df.img[i]}")
                        st.info(f"{df.figure[i]}: {df.caption[i]}")

    elif selected_tab == "Checklist":
    
        # Step 1
        st.header("✅ Checklist")
        st.markdown("### Step 1: Consular processing or Adjustment of Status processing")
        st.markdown("##### Determine your eligibility for either consular processing or adjustment of status based on your circumstances and location.")
        topics_step1 = [
            "Consular",
            "Adjustment of Status",
        ]
        checklist_step1 = [st.checkbox(topic) for topic in topics_step1]

        # Step 2
        st.markdown("### Step 2: Determine Your Eligibility for EB2-NIW Visa")
        st.markdown("##### Possess an advanced degree (masters, doctorate, or bachelor's degree plus five years of progressive work experience), or possess exceptional ability in your field.")

        ad_nodes = []
        ea_nodes = []
        
        advanced_degree = st.checkbox("Advanced Degree - check only one option:")
        if advanced_degree:
            ad_nodes = [
                {"label": "Hold a U.S. master's degree or higher (or its foreign equivalent) in the field where you intend to work", "value": "masters"},
                {"label": "Hold a U.S. bachelor's degree (or its foreign equivalent) and have at least five years of progressive post-bachelor work experience in your field", "value": "bachelors"},
            ]
            return_select_ad_nodes = tree_select(ad_nodes, no_cascade=True, key="ad_nodes")

        exceptional_ability = st.checkbox("Exceptional Ability:")
        if exceptional_ability:
            ea_nodes = [
                {"label": "Meet at least three of the following criteria: official academic records, letters documenting at least ten years of full-time experience, a license or certification, evidence of salary or service remuneration, membership in professional associations, recognition for achievements and significant contributions, or comparable evidence of eligibility."},
            ]
            return_select_ea_nodes = tree_select(ea_nodes, no_cascade=True, key="ea_nodes")
            
        # Step 3
        st.markdown("### Step 3: Filling the Forms")
        adjustment_of_status = st.checkbox("For Adjustment of Status:")
        
        nodes_step3 = []
        nodes_step3b = []
        
        if adjustment_of_status:
            nodes_step3 = [
                {"label": "Form I-140 (petitioner only)", "value":"I140"},
                {"label": "Form ETA-750B (optional but recommended, petitioner only)", "value":"750B"},
                {"label": "Form I-485 (petitioner and dependents)", "value":"I485"},
                {"label": "Form I-765 (petitioner and dependents)", "value":"I765"},
                {"label": "Form I-131 (petitioner and dependents, optional)", "value":"I131"},
                {"label": "Form G-1145 (petitioner and dependents)", "value":"G1145"},
            ]
            return_select_nodes_step3 = tree_select(nodes_step3, no_cascade=True, key="nodes_step3")

        consular_processing = st.checkbox("For Consular Processing:")
        if consular_processing:
            nodes_step3b = [
                {"label": "Form I-140 (petitioner only)", "value":"I140"},
                {"label": "Form ETA-750B (optional but recommended, petitioner only)", "value":"750"},
            ]
            return_select_nodes_step3b = tree_select(nodes_step3b, no_cascade=True, key="nodes_step3b")


        # Step 4
        st.markdown("### Step 4: Gather the Required Personal Documentation")
        st.markdown("##### Step 4.1: Make sure to gather these documents for yourself and any dependents (spouse and unmarried children under 21 years old) who will be included in your EB2-NIW application.")

        step4_required_documents = [
            "Valid passport with an expiration date at least six months later",
            "Copy of your birth certificate and certified translation if it is not in English",
            "Copy of your marriage certificate and certified translation if it is not in English (if applicable)",
            "Copies of any divorce decrees or annulment documents from previous marriages, along with certified translations if they are not in English (if applicable)",
        ]
        checklist_step4 = [st.checkbox(doc) for doc in step4_required_documents]

        st.markdown("##### Step 4.2: If you and your dependents (spouse and unmarried children under 21 years old) are currently living in the United States under a temporary visa and are applying for an EB2-NIW adjustment, you will need to provide documentation related to your current visa status. This may include:")

        step4_us_temp_visa = [
            "Copy of your Form I-94, Arrival/Departure Record, or other evidence of lawful entry into the United States (if applicable)",
            "Evidence of your current visa status, such as a copy of your current visa, approval notice, or Employment Authorization Document (EAD) (if applicable)",
            "Other relevant documents related to your current visa status, such as your F1 visa and I-20 (for students), temporary work visa, or other relevant documents (if applicable)",
        ]
        checklist_step4_us_temp_visa = [st.checkbox(doc) for doc in step4_us_temp_visa]
        
            # Step 5
        st.markdown("### Step 5: Elaborating your Resume")
        step5_resume_tips = [
            "Start with a clear and concise summary",
            "Focus on your achievements",
            "Use metrics to quantify your accomplishments",
            "Tailor your resume to the EB2-NIW criteria",
            "Include relevant work experience",
            "Proofread and edit",
        ]
        checklist_step5 = [st.checkbox(tip) for tip in step5_resume_tips]

        # Step 6
        st.markdown("### Step 6: Gathering documentation to substantiate the experiences and achievements highlighted in your resume")
        st.markdown("##### Ensuring that your resume is supported by proper documentation can increase your chances of success in the EB2-NIW application process. Here are some examples of how you can substantiate your professional experiences when applying for EB2-NIW:")

        step6_documentation = [
            "Publications",
            "Patents",
            "Awards and recognition",
            "Education and training",
            "Letters of recommendation",
            "Employment letter",
        ]
        checklist_step6 = [st.checkbox(doc) for doc in step6_documentation]

            # Step 7
        st.markdown("### Step 7: Documentation that will evidence your advanced degree or exceptional ability")
        
        advanced_degree_docs = st.checkbox("For Advanced Degree:")
        nodes_step7a = []
        nodes_step7b = []
        
        if advanced_degree_docs:
            nodes_step7a = [
                {"label": "Official academic records", "value":"academic"},
                {"label": "Credentials evaluation (if applicable)", "value":"credentials"},
                {"label": "Employment experience", "value":"experience"},
            ]
            return_select_nodes_step7a = tree_select(nodes_step7a, no_cascade=True, key="nodes_step7a")

        exceptional_ability_docs = st.checkbox("For Exceptional Ability:")
        if exceptional_ability_docs:
            nodes_step7b = [
                {"label": "Academic records", "value":"academic"},
                {"label": "Employment experience", "value":"employment"},
                {"label": "Professional license or certification", "value":"license"},
                {"label": "Salary history", "value":"salary"},
                {"label": "Professional association membership", "value":"professional"},
                {"label": "Recognition for achievements", "value":"recognition"},
                {"label": "Other comparable evidence", "value":"other"},
            ]
            return_select_nodes_step7b = tree_select(nodes_step7b, no_cascade=True, key="nodes_step7b")

        # Step 8
        st.markdown("### Step 8: Documentation to evidence you qualify for NIW National Interest Waiver")

        step8_documentation = [
            "Professional Plan",
            "Business Plan",
        ]
        
        checklist_step8 = [st.checkbox(doc) for doc in step8_documentation]
        
        support_letters_docs = st.checkbox("Support Letters")
        nodes_step8 = []
        if support_letters_docs:
            nodes_step8 = [
                {"label": "Recommendation letter 1 and resume", "value":"letterone"},
                {"label": "Recommendation letter 2 and resume", "value":"lettertwo"},
                {"label": "Recommendation letter 3 and resume", "value":"letterthree"},
                {"label": "Recommendation letter 4 and resume", "value":"letterfour"},
                {"label": "Recommendation letter 5 and resume", "value":"letterfive"},
                {"label": "Intention letter 1 and resume", "value":"intentionone"},
                {"label": "Intention letter 2 and resume", "value":"intentiontwo"},
                {"label": "Intention letter 3 and resume", "value":"intentionthree"},
            ]
            return_select_nodes_step8 = tree_select(nodes_step8, no_cascade=True, key="nodes_step8")

        # Step 9
        st.markdown("### Step 9: Writing the Cover Letter")
        topics_step9 = [
            "Introduce yourself and state the purpose of the letter",
            "Advanced Degree or Exceptional Ability Section",
            "National Interest Waiver Section",
            "Substantial Merit and National Importance",
            "Well-positioned to advance the Proposed Endeavor",
            "It would benefit the United States to waive the labor certification",
            "Conclusion",
        ]
        checklist_step9 = [st.checkbox(topic) for topic in topics_step9]

        # Step 10
        st.markdown("### Step 10: Elaborating the Table of Contents")
        topics_step10 = [
            "Create a detailed table of contents",
        ]
        checklist_step10 = [st.checkbox(topic) for topic in topics_step10]

        # Step 11
        st.markdown("### Step 11: Prepare your application package for EB-2 NIW")
        topics_step11 = [
            "Create a cover page for your EB-2 NIW package",
            "Arrange the documents in the same order as they appear in the Table of Contents",
            "Place a cover page before each section with the following titles: I. Forms, II. Personal Documents, III. Cover Letter, IV. Eligibility Criteria: Advanced Degree / Exceptional Ability, V. National Interest Waiver, VI. Additional Supporting Materials.",
            "Attach small adhesive labels to the edges of each Exhibit cover page, with the exhibit number marked on the label",
            "Ensure that the exhibit labels are placed along the edge of the page to allow them to be easily visible and readable when the binder is closed",
            "Avoid placing the exhibit labels one behind the other to allow the USCIS officer to view all of them when the binder is closed",
            "Label each exhibit with its corresponding exhibit number",
        ]
        checklist_step11 = [st.checkbox(topic) for topic in topics_step11]

        # Step 12
        st.markdown("### Step 12: Submit your EB2-NIW case")
        topics_step12 = [
            "Review your application package to ensure that it is complete and that all required forms and documents are included",
            "Make a copy of the entire application package for your records",
            "Pay the filing fees",
            "Submit your application package to the appropriate USCIS lockbox facility",
            "Track the status of your application",
            "Respond promptly to any requests for additional information or evidence from USCIS",
        ]
        checklist_step12 = [st.checkbox(topic) for topic in topics_step12]
        
        # Check if I'm ready button
        def tree_is_checked(nodes, checked_nodes):
            result = []

            def traverse(node_list):
                for node in node_list:
                    if 'children' in node:
                        traverse(node['children'])
                    elif node['value'] in checked_nodes:
                        result.append(node['value'])

            traverse(nodes)
            return result

        return_select_ad_nodes = {'checked': []} if 'checked' not in locals() else return_select_ad_nodes
        checked_nodes_ad_nodes = return_select_ad_nodes['checked'] if 'checked' in return_select_ad_nodes else []
        return_select_ea_nodes = {'checked': []} if 'checked' not in locals() else return_select_ea_nodes
        checked_nodes_ea_nodes = return_select_ea_nodes['checked'] if 'checked' in return_select_ea_nodes else []
        return_select_nodes_step3 = {'checked': []} if 'checked' not in locals() else return_select_nodes_step3
        checked_nodes_step3 = return_select_nodes_step3['checked'] if 'checked' in return_select_nodes_step3 else []
        return_select_nodes_step3b = {'checked': []} if 'checked' not in locals() else return_select_nodes_step3b
        checked_nodes_step3b = return_select_nodes_step3b['checked'] if 'checked' in return_select_nodes_step3b else []
        return_select_nodes_step7a = {'checked': []} if 'checked' not in locals() else return_select_nodes_step7a
        checked_nodes_step7a = return_select_nodes_step7a['checked'] if 'checked' in return_select_nodes_step7a else []
        return_select_nodes_step7b = {'checked': []} if 'checked' not in locals() else return_select_nodes_step7b
        checked_nodes_step7b = return_select_nodes_step7b['checked'] if 'checked' in return_select_nodes_step7b else []
        return_select_nodes_step8 = {'checked': []} if 'checked' not in locals() else return_select_nodes_step8
        checked_nodes_step8 = return_select_nodes_step8['checked'] if 'checked' in return_select_nodes_step8 else []


        # Check if I'm ready button
        ready_button = st.button("Check if I'm ready")

        def tree_is_checked(nodes, checked_nodes):
            result = []

            def traverse(node_list):
                for node in node_list:
                    if 'children' in node:
                        traverse(node['children'])
                    elif node['value'] in checked_nodes:
                        result.append(node['value'])

            traverse(nodes)
            return result

        if ready_button:
            # Check rules for each step
            step1_check = sum(checklist_step1) == 1
            step2_check = (advanced_degree and all(value in checked_nodes_ad_nodes for value in tree_is_checked(ad_nodes, checked_nodes_ad_nodes))) or (exceptional_ability and all(value in checked_nodes_ea_nodes for value in tree_is_checked(ea_nodes, checked_nodes_ea_nodes)))
            step3_check = (adjustment_of_status and all(tree_is_checked(nodes_step3, checked_nodes_step3))) or (consular_processing and all(tree_is_checked(nodes_step3b, checked_nodes_step3b)))
            step4_check = all(checklist_step4) and all(checklist_step4_us_temp_visa)
            step5_check = all(checklist_step5)
            step6_check = all(checklist_step6)
            step7_check = (advanced_degree_docs and all(tree_is_checked(nodes_step7a, checked_nodes_step7a))) or (exceptional_ability_docs and all(tree_is_checked(nodes_step7b, checked_nodes_step7b)))
            step8_check = all(checklist_step8) and all(tree_is_checked(nodes_step8, checked_nodes_step8))
            step9_check = all(checklist_step9)
            step10_check = all(checklist_step10)
            step11_check = all(checklist_step11)
            step12_check = all(checklist_step12)

            all_checks = [
                step1_check,
                step2_check,
                step3_check,
                step4_check,
                step5_check,
                step6_check,
                step7_check,
                step8_check,
                step9_check,
                step10_check,
                step11_check,
                step12_check,
            ]

            # Display the result
            if all(all_checks):
                st.success("You are ready to apply!")
            else:
                st.error("You have missing steps.")

    elif selected_tab == "EB2Visaticket assistant":
        import os
        cwd = os.getcwd()
        os.environ['PYTORCH_TRANSFORMERS_CACHE'] = os.path.join(cwd, 'ai_advisor/huggingface/transformers/')
        os.environ['TRANSFORMERS_CACHE'] = os.path.join(cwd, 'ai_advisor/huggingface/transformers/')
        os.environ['HF_HOME'] = os.path.join(cwd, 'ai_advisor/huggingface/')
        # import sys
        import logging
        from json import JSONDecodeError
        from pathlib import Path

        # import zipfile
        import pandas as pd
        import streamlit as st
        from markdown import markdown

        from ai_advisor_tmp.utils import get_backlink, get_pipelines, query, send_feedback, upload_doc

        # Adjust to a question that you would like users to see in the search bar when they load the UI:
        DEFAULT_QUESTION_AT_STARTUP = os.getenv(
            "DEFAULT_QUESTION_AT_STARTUP", "How to get EAD?")
        DEFAULT_ANSWER_AT_STARTUP = os.getenv(
            "DEFAULT_ANSWER_AT_STARTUP", "You must file a Form I-765")

        # Sliders
        DEFAULT_DOCS_FROM_RETRIEVER = int(
            os.getenv("DEFAULT_DOCS_FROM_RETRIEVER", "5"))
        DEFAULT_NUMBER_OF_ANSWERS = int(os.getenv("DEFAULT_NUMBER_OF_ANSWERS", "1"))


        # Whether the file upload should be enabled or not
        DISABLE_FILE_UPLOAD = bool(os.getenv("DISABLE_FILE_UPLOAD", "True"))

        LANG_MAP = {"English": "English", "Ukrainian": "Ukrainian", "russian": "russian"}


        pipelines = get_pipelines()


        def set_state_if_absent(key, value):
            if key not in st.session_state:
                st.session_state[key] = value
        # Persistent state
        set_state_if_absent("question", DEFAULT_QUESTION_AT_STARTUP)
        set_state_if_absent("answer", DEFAULT_ANSWER_AT_STARTUP)
        set_state_if_absent("results", None)
        set_state_if_absent("raw_json", None)
        set_state_if_absent("random_question_requested", False)

        # Small callback to reset the interface in case the text of the question changes
        def reset_results(*args):
            st.session_state.answer = None
            st.session_state.results = None
            st.session_state.raw_json = None

        # Title
        st.markdown("""
            <div style="display:flex; justify-content:center;">
                <h1>🇺🇸 EB2-NIW Application Process Tutorial</h1>
            </div>""", unsafe_allow_html=True)

        # Sidebar
        language = st.selectbox(
            "Select language: ", ("English", "Spanish", "French", "Italian", "Arabic", "Hindi", "Portuguese", "Mandarin Chinese"))
        debug = False
        # debug = st.sidebar.checkbox("Show debug info")
        if debug:
            top_k_reader = st.sidebar.slider(
                "Max. number of answers",
                min_value=1,
                max_value=100,
                value=DEFAULT_NUMBER_OF_ANSWERS,
                step=1,
                on_change=reset_results,
            )

            top_k_retriever = st.sidebar.slider(
                "Max. number of documents from retriever",
                min_value=1,
                max_value=100,
                value=DEFAULT_DOCS_FROM_RETRIEVER,
                step=1,
                on_change=reset_results,
            )
        else:
            top_k_reader = DEFAULT_NUMBER_OF_ANSWERS
            top_k_retriever = DEFAULT_DOCS_FROM_RETRIEVER
        # File upload block
        if not DISABLE_FILE_UPLOAD:
            st.sidebar.write("## File Upload:")
            data_files = st.sidebar.file_uploader(
                "", type=["pdf", "txt", "docx"], accept_multiple_files=True)
            for data_file in data_files:
                # Upload file
                if data_file:
                    raw_json = upload_doc(data_file)
                    st.sidebar.write(str(data_file.name) + " &nbsp;&nbsp; ✅ ")
                    if debug:
                        st.subheader("REST API JSON response")
                        st.sidebar.write(raw_json)

        # Search bar
        question = st.text_input(
            "", value=st.session_state.question, max_chars=100, on_change=reset_results)
      
        col1, col2 = st.columns(2)
        col1.markdown(
            "<style>.stButton button {width:50%;}</style>", unsafe_allow_html=True)
        col2.markdown(
            "<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)

        # Run button
        run_pressed = col1.button("Find your answer")

        run_query = (
            run_pressed or question != st.session_state.question
        ) and not st.session_state.random_question_requested

        # Get results for query
        if run_query and question:
            reset_results()
            st.session_state.question = question

            with st.spinner("🧠 &nbsp;&nbsp; Gathering data and providing you with the best answer... \n "):
                try:
                    st.session_state.results, st.session_state.raw_json = query(
                        pipelines, question, top_k_reader=top_k_reader, top_k_retriever=top_k_retriever, language=language
                    )
                except JSONDecodeError as je:
                    st.error(
                        "👓 &nbsp;&nbsp; An error occurred reading the results. Is the document store working?")
                  
                except Exception as e:
                    logging.exception(e)
                    if "The server is busy processing requests" in str(e) or "503" in str(e):
                        st.error(
                            "🧑‍🌾 &nbsp;&nbsp; All our workers are busy! Try again later.")
                    else:
                        st.error(
                            "🐞 &nbsp;&nbsp; An error occurred during the request.")
                

        if st.session_state.results:

            st.write("## Results:")

            for count, result in enumerate(st.session_state.results):
                if result["answer"]:
                    answer, context = result["answer"], result["context"]
                    start_idx = context.find(answer)
                    end_idx = start_idx + len(answer)
                    # Hack due to this bug: https://github.com/streamlit/streamlit/issues/3190
                    st.write(
                        markdown(f"**Answer:** {answer}"), unsafe_allow_html=True)

                    source = ""
                    url, title = get_backlink(result)
                    if url and title:
                        source = f"[{result['document']['meta']['title']}]({result['document']['meta']['url']})"
                    else:
                        source = f"{result['source']}"
                    st.markdown(f"**Source:** {source}")

                else:
                    st.info(
                        "🤔 &nbsp;&nbsp; Unsure whether any of the documents contain an answer to your question. Try to reformulate it!"
                    )

                st.write("___")

else:
    if st.session_state["authenticated"]:
        st.write("You do not have access. Please contact the administrator.")
    else:
        st.write("Please login!")
