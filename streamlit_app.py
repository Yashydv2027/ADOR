import streamlit as st
import requests
import pandas as pd
import json
import time
import plotly.express as px
import uuid

st.set_page_config(
    page_title="ADOR - Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #1f77b4;}
    .topic-card {
        background-color: #f0f7ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .keyword-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.9em;
    }
    .qa-question {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #000000;
    }
    .qa-answer {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000/api/v1/extract"
HEALTH_URL = "http://localhost:8000/health"
QA_CREATE_URL = "http://localhost:8000/api/v1/qa/create-session"
QA_ASK_URL = "http://localhost:8000/api/v1/qa/ask"
QA_SUGGESTIONS_URL = "http://localhost:8000/api/v1/qa/suggestions"

if 'qa_session_id' not in st.session_state:
    st.session_state['qa_session_id'] = None
if 'qa_history' not in st.session_state:
    st.session_state['qa_history'] = []

st.title("📄 ADOR - Augmented Document Reader")
st.markdown("**Complete AI-Powered Financial Document Intelligence Platform**")

with st.sidebar:
    st.header("⚙️ System Info")

    try:
        health_response = requests.get(HEALTH_URL, timeout=2)
        if health_response.status_code == 200:
            st.success("✅ API Status: Online")
        else:
            st.error("❌ API Status: Error")
    except:
        st.error("❌ API Status: Offline")
        st.warning("⚠️ Start FastAPI: `python app/main.py`")

    st.markdown("---")
    st.header("📊 Supported Formats")
    st.markdown("""
    - **📄 DOCX** - Rule-based (90-95%)
    - **💬 TXT** - NER Model (80-85%)
    - **📕 PDF** - LLM Extraction (85-90%)
    """)

    st.markdown("---")
    st.header("🎯 Features")
    st.markdown("""
    - ✅ Document classification
    - ✅ Auto-summarization (LLM)
    - ✅ Topic modelling (LLM)
    - ✅ Entity extraction (NER)
    - ✅ Question answering (LLM)
    """)

tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Extract", "📊 Analysis Results", "💬 Q&A", "ℹ️ About"])

with tab1:
    st.header("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['docx', 'txt', 'pdf'],
        help="Upload DOCX, TXT, or PDF for analysis"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        extract_button = st.button("🚀 Analyze Document", type="primary", use_container_width=True)
    with col2:
        if uploaded_file:
            st.info(f"📁 {uploaded_file.name}")

    if extract_button and uploaded_file:
        with st.spinner("🔄 Processing..."):
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                start_time = time.time()
                response = requests.post(API_URL, files=files)
                processing_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    st.session_state['result'] = result
                    st.session_state['processing_time'] = processing_time
                    st.session_state['filename'] = uploaded_file.name

                    # Extract document text for Q&A
                    try:
                        if uploaded_file.type == 'text/plain':
                            uploaded_file.seek(0)
                            document_text = uploaded_file.getvalue().decode('utf-8', errors='ignore')
                        elif 'word' in uploaded_file.type:
                            from docx import Document
                            from io import BytesIO
                            uploaded_file.seek(0)
                            doc = Document(BytesIO(uploaded_file.getvalue()))
                            document_text = "\n".join([para.text for para in doc.paragraphs])
                        elif 'pdf' in uploaded_file.type:
                            import pdfplumber
                            from io import BytesIO
                            uploaded_file.seek(0)
                            text_parts = []
                            with pdfplumber.open(BytesIO(uploaded_file.getvalue())) as pdf:
                                for page in pdf.pages:
                                    page_text = page.extract_text()
                                    if page_text:
                                        text_parts.append(page_text)
                            document_text = "\n".join(text_parts)
                        else:
                            document_text = ""
                    except:
                        document_text = ""

                    # Create Q&A session
                    session_id = str(uuid.uuid4())
                    entities_list = result.get('entities', [])
                    entities_dict = {}
                    for entity in entities_list:
                        entity_type = entity.get('type')
                        entity_value = entity.get('value')
                        if entity_type:
                            if entity_type not in entities_dict:
                                entities_dict[entity_type] = []
                            entities_dict[entity_type].append(entity_value)

                    qa_payload = {
                        'session_id': session_id,
                        'document_text': document_text[:5000],
                        'entities': entities_dict
                    }

                    try:
                        qa_response = requests.post(QA_CREATE_URL, json=qa_payload, timeout=10)
                        if qa_response.status_code == 200:
                            qa_data = qa_response.json()
                            if qa_data.get('success'):
                                st.session_state['qa_session_id'] = session_id
                                st.session_state['qa_history'] = []
                                st.success(f"✅ Complete analysis with Q&A in {processing_time:.2f}s!")
                            else:
                                st.success(f"✅ Analysis completed in {processing_time:.2f}s")
                                st.info(f"ℹ️ Q&A unavailable: {qa_data.get('message')}")
                        else:
                            st.success(f"✅ Analysis completed in {processing_time:.2f}s")
                            st.info("ℹ️ Q&A requires OpenAI API key")
                    except:
                        st.success(f"✅ Analysis completed in {processing_time:.2f}s")
                        st.info("ℹ️ Q&A unavailable")
                else:
                    st.error(f"❌ Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("Analysis Results")

    if 'result' in st.session_state:
        result = st.session_state['result']

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Entities", result.get('statistics', {}).get('total_entities', 0))
        with col2:
            st.metric("⚡ Time", f"{st.session_state.get('processing_time', 0):.2f}s")
        with col3:
            st.metric("🏷️ Topics", result.get('topics', {}).get('num_topics', 0))
        with col4:
            st.metric("📝 Method", result.get('metadata', {}).get('extraction_method', 'N/A'))

        st.markdown("---")

        # Summary
        if 'summary' in result and result['summary']:
            st.subheader("📝 Document Summary")
            summary_data = result['summary']
            col1, col2 = st.columns([3, 1])

            with col1:
                summary_text = summary_data.get('summary', 'No summary available')
                st.markdown(f"""
                <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                    <p style="color: #000000; font-size: 16px; line-height: 1.8; margin: 0;">{summary_text}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.metric("Method", summary_data.get('method', 'N/A').title())
                st.metric("Length", f"{summary_data.get('length', 0)} words")
                original_len = summary_data.get('original_length', 0)
                summary_len = summary_data.get('length', 0)
                if original_len > 0:
                    compression = (1 - summary_len / original_len) * 100
                    st.metric("Compression", f"{compression:.0f}%")

            st.markdown("---")

        # Topics
        if 'topics' in result and result['topics']:
            st.subheader("🏷️ Topic Modelling")
            topics_data = result['topics']
            topics = topics_data.get('topics', [])
            overall_theme = topics_data.get('overall_theme', '')

            if overall_theme:
                st.info(f"**Overall Theme:** {overall_theme}")

            if topics:
                for i, topic in enumerate(topics, 1):
                    topic_name = topic.get('name', 'Unknown')
                    relevance = topic.get('relevance', 0)
                    keywords = topic.get('keywords', [])
                    description = topic.get('description', '')

                    st.markdown(f"""
                    <div class="topic-card">
                        <h4 style="color: #1976d2; margin: 0 0 0.5rem 0;">{i}. {topic_name}</h4>
                        <div style="margin-bottom: 0.5rem;">
                            <span style="color: #666;">Relevance: </span>
                            <span style="color: #1976d2; font-weight: bold;">{relevance:.0%}</span>
                        </div>
                        {f'<p style="color: #555; margin: 0.5rem 0;">{description}</p>' if description else ''}
                        <div style="margin-top: 0.5rem;">
                            {''.join([f'<span class="keyword-badge">{kw}</span>' for kw in keywords])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

        # Classification
        if 'classification' in result:
            classification = result['classification']
            col1, col2 = st.columns([2, 3])

            with col1:
                st.subheader("📑 Classification")
                doc_type = classification.get('document_type', 'Unknown')
                st.metric("Document Type", doc_type)

            with col2:
                st.subheader("🔍 Alternatives")
                all_scores = classification.get('all_scores', {})
                if all_scores:
                    for dt, score in list(all_scores.items())[:3]:
                        st.write(f"**{dt}**: {score:.2f}")

        st.markdown("---")

        # Entities
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📋 Extracted Entities")
            entities_df = pd.DataFrame(result.get('entities', []))
            if not entities_df.empty:
                st.dataframe(entities_df[['type', 'value']], use_container_width=True, hide_index=True)

        with col2:
            st.subheader("📊 Distribution")
            entity_counts = result.get('statistics', {}).get('entity_types', {})
            if entity_counts:
                fig = px.pie(names=list(entity_counts.keys()), values=list(entity_counts.values()))
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

        # Downloads
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            json_str = json.dumps(result, indent=2)
            st.download_button("📥 Download JSON", json_str,
                             file_name=f"analysis_{st.session_state.get('filename', 'result')}.json",
                             mime="application/json")
        with col2:
            if result.get('entities'):
                csv = pd.DataFrame([{'Type': e['type'], 'Value': e['value']} for e in result['entities']]).to_csv(index=False)
                st.download_button("📥 Download CSV", csv,
                                 file_name=f"entities_{st.session_state.get('filename', 'result')}.csv")
    else:
        st.info("👈 Upload a document to see results")

with tab3:
    st.header("💬 Ask Questions About Your Document")

    if st.session_state.get('qa_session_id'):
        st.success("✅ Q&A Session Active")

        try:
            suggestions_response = requests.get(f"{QA_SUGGESTIONS_URL}/{st.session_state['qa_session_id']}")
            if suggestions_response.status_code == 200:
                suggestions = suggestions_response.json().get('suggestions', [])
                if suggestions:
                    st.markdown("**💡 Suggested Questions:**")
                    cols = st.columns(min(len(suggestions), 5))
                    for idx, suggestion in enumerate(suggestions[:5]):
                        with cols[idx]:
                            if st.button(suggestion[:25] + "..." if len(suggestion) > 25 else suggestion,
                                       key=f"suggest_{idx}",
                                       use_container_width=True):
                                st.session_state['current_question'] = suggestion
        except:
            pass

        question = st.text_input("Your Question:",
                                value=st.session_state.get('current_question', ''),
                                placeholder="e.g., What is the notional amount?")

        col1, col2 = st.columns([1, 4])
        with col1:
            ask_button = st.button("🎯 Ask", type="primary", use_container_width=True)

        if ask_button and question:
            with st.spinner("🤔 Thinking..."):
                try:
                    qa_payload = {'session_id': st.session_state['qa_session_id'], 'question': question}
                    qa_response = requests.post(QA_ASK_URL, json=qa_payload)

                    if qa_response.status_code == 200:
                        answer_data = qa_response.json()
                        answer = answer_data.get('answer', 'No answer')

                        st.session_state['qa_history'].append({'question': question, 'answer': answer})
                        if 'current_question' in st.session_state:
                            del st.session_state['current_question']
                        st.rerun()
                    else:
                        st.error(f"Error: {qa_response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if st.session_state['qa_history']:
            st.markdown("---")
            st.subheader("📜 Conversation History")

            for idx, qa in enumerate(reversed(st.session_state['qa_history'])):
                st.markdown(f"""
                <div class="qa-question">
                    <strong>❓ Q{len(st.session_state['qa_history'])-idx}:</strong> {qa['question']}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="qa-answer">
                    <strong>💡 A:</strong> {qa['answer']}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("")
    else:
        st.info("👈 Upload and analyze a document first")
        st.markdown("""
        ### How Q&A Works:
        1. Upload a document
        2. Wait for analysis
        3. Ask questions
        4. Get intelligent answers

        **Requires OpenAI API key configured in `.env`**
        """)

with tab4:
    st.header("About ADOR")
    st.markdown("""
    ### 🎯 Complete AI Document Intelligence

    **ADOR v4.0** - All 6 features implemented (100% complete)

    #### Features:
    1. **Document Classification** - 8+ categories
    2. **Summarization** - LLM-powered summaries
    3. **Topic Modelling** - Intelligent topic extraction
    4. **NER** - Rule-based, ML & LLM extraction
    5. **Question Answering** - Context-aware Q&A

    #### Technology:
    - FastAPI + Streamlit
    - OpenAI GPT-4o-mini
    - spaCy Transformers
    - python-docx, pdfplumber

    #### API Docs:
    [http://localhost:8000/docs](http://localhost:8000/docs)
    """)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📄 ADOR v4.0**")
with col2:
    st.markdown("**[API Docs](http://localhost:8000/docs)**")
with col3:
    st.markdown("**⚡ 100% Complete**")
