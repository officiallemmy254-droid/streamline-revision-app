

































import streamlit as st
import google.generativeai as genai
import PyPDF2
import numpy as np
import os

# Page Config
st.set_page_config(page_title="Teacher Revision Skill", layout="wide", page_icon="🍎")

# Custom CSS for a better look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for Config
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Google Gemini API Key", type="password", help="Get your API key from https://aistudio.google.com/app/apikey")
    if api_key:
        genai.configure(api_key=api_key)
    
    st.markdown("---")
    st.markdown("### Instructions")
    st.write("1. Enter your Gemini API Key.")
    st.write("2. Upload your Teaching Diploma PDF.")
    st.write("3. Generate a classroom scenario.")
    st.write("4. Apply your knowledge and get feedback.")
    
    st.markdown("---")
    st.info("This tool follows 'Minimal Risk' AI guidelines. It focuses on educational support and does not store personal data.")

# Load skill.md logic
def load_skill_logic():
    try:
        with open("skill.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading skill logic: {e}"

skill_logic = load_skill_logic()

# Helper: PDF Text Extraction
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# Helper: Chunking
def chunk_text(text, chunk_size=1500, overlap=300):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Helper: Simple RAG Retrieval
def get_embeddings(texts):
    if not api_key:
        return None
    try:
        # Gemini embedding model
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=texts,
            task_type="retrieval_document"
        )
        return np.array(result['embedding'])
    except Exception as e:
        st.error(f"Embedding error: {e}")
        return None

def find_relevant_chunks(query, chunks, chunk_embeddings, top_k=3):
    try:
        query_embedding_res = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = np.array(query_embedding_res['embedding'])
        
        # Cosine similarity calculation
        dot_product = np.dot(chunk_embeddings, query_embedding)
        norm_chunks = np.linalg.norm(chunk_embeddings, axis=1)
        norm_query = np.linalg.norm(query_embedding)
        similarities = dot_product / (norm_chunks * norm_query)
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [chunks[i] for i in top_indices]
    except Exception as e:
        st.error(f"Retrieval error: {e}")
        return chunks[:top_k] # Fallback to first few chunks

# UI Main
st.title("🍎 Teacher Revision Skill")
st.markdown("#### *Bridge the gap between Diploma Theory and Classroom Practice*")

if not api_key:
    st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar to begin.")

uploaded_file = st.file_uploader("Upload Teaching Diploma PDF (Course notes, textbooks, or frameworks)", type="pdf")

if uploaded_file and api_key:
    # Use the filename as a key to reset if a new file is uploaded
    if "file_name" not in st.session_state or st.session_state.file_name != uploaded_file.name:
        with st.spinner("Analyzing PDF content... (In-memory indexing)"):
            raw_text = extract_text_from_pdf(uploaded_file)
            if not raw_text.strip():
                st.error("Could not extract text from this PDF. It might be scanned or protected.")
            else:
                chunks = chunk_text(raw_text)
                embeddings = get_embeddings(chunks)
                if embeddings is not None:
                    st.session_state.chunks = chunks
                    st.session_state.embeddings = embeddings
                    st.session_state.file_name = uploaded_file.name
                    st.session_state.current_scenario = None
                    st.session_state.feedback = None
                    st.success(f"Successfully indexed '{uploaded_file.name}'")

    if "chunks" in st.session_state:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🛠️ Practice Area")
            if st.button("✨ Generate New Scenario"):
                with st.spinner("Designing a classroom dilemma based on your PDF..."):
                    # Retrieve random chunks or general pedagogical chunks to seed the scenario
                    seed_query = "fundamental teaching principles and classroom challenges"
                    relevant_context = find_relevant_chunks(seed_query, 
                                                           st.session_state.chunks, 
                                                           st.session_state.embeddings)
                    context_str = "\n".join(relevant_context)
                    
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    SYSTEM LOGIC (skill.md):
                    {skill_logic}
                    
                    PDF CONTEXT:
                    {context_str}
                    
                    TASK: Based on the Persona and Scenario Generator logic in the skill.md, create a new Classroom Dilemma. Ensure it is grounded in the provided PDF context but does not explicitly name the underlying theories.
                    """
                    response = model.generate_content(prompt)
                    st.session_state.current_scenario = response.text
                    st.session_state.feedback = None
                    st.rerun()

            if st.session_state.get("current_scenario"):
                st.info(st.session_state.current_scenario)
                
                user_answer = st.text_area("Your Pedagogical Response:", placeholder="I would use scaffolding by...", height=250)
                
                if st.button("🚀 Get Qualitative Feedback"):
                    if user_answer:
                        with st.spinner("Evaluating your approach against the PDF's theories..."):
                            # Retrieve chunks relevant to the user's answer for precise feedback
                            relevant_context = find_relevant_chunks(user_answer, 
                                                                   st.session_state.chunks, 
                                                                   st.session_state.embeddings)
                            context_str = "\n".join(relevant_context)
                            
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            prompt = f"""
                            SYSTEM LOGIC (skill.md):
                            {skill_logic}
                            
                            PDF CONTEXT:
                            {context_str}
                            
                            SCENARIO GIVEN:
                            {st.session_state.current_scenario}
                            
                            USER'S ANSWER:
                            {user_answer}
                            
                            TASK: Provide qualitative feedback using the Feedback Loop logic in skill.md. Focus on theory-to-practice alignment and provide 'Next Steps'. Do not give a numerical grade.
                            """
                            response = model.generate_content(prompt)
                            st.session_state.feedback = response.text
                            st.rerun()
                    else:
                        st.warning("Please type your response before submitting.")

        with col2:
            st.markdown("### 🎓 Feedback & Reflection")
            if st.session_state.get("feedback"):
                st.markdown(st.session_state.feedback)
            else:
                st.write("Generate a scenario and submit your response to see expert feedback here.")

else:
    st.info("👆 Upload a PDF to begin your revision session.")

st.markdown("---")
st.caption("Built for Anti-gravity IDE | Powered by Google Gemini 1.5 Flash")
