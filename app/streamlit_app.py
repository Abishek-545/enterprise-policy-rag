import os
import sys
from pathlib import Path

import streamlit as st

try:
    for key in ("GROQ_API_KEY", "GROQ_MODEL", "EMBEDDING_MODEL", "TOP_K"):
        if key in st.secrets and not os.getenv(key):
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag_app.config import get_settings
from rag_app.ingest import ingest_directory
from rag_app.pipeline import answer_question
from rag_app.vector_store import ChromaVectorStore

SAMPLE_DOCS = PROJECT_ROOT / "data" / "sample_docs"

CAPABILITIES = [
    "Leave balance rules, sick leave, vacation carryover, approval timing, and holiday coverage",
    "Workplace safety, emergency response, incident reporting, visitors, and contractor rules",
    "Employee conduct, harassment reporting, conflicts of interest, gifts, and company asset use",
    "Security, data classification, password rules, device safety, AI tool use, and breach reporting",
    "Travel booking, meal limits, receipt rules, pre-approval thresholds, and reimbursement policy",
]

SUGGESTED_QUESTIONS = [
    "How many vacation days can a full-time employee carry over?",
    "When should a security incident be reported?",
    "What expenses require manager approval?",
    "What should employees do during an emergency evacuation?",
    "Are employees allowed to paste confidential data into external AI tools?",
    "What gifts from vendors require Legal review?",
]

POLICY_AREAS = {
    "Leave & Vacation": "PTO, sick leave, parental leave, bereavement, holidays, carryover",
    "Safety": "Hazards, emergency response, incident reports, remote-work safety",
    "Conduct": "Respectful workplace, conflicts, gifts, assets, discipline",
    "Security": "Data classes, MFA, devices, incidents, third parties, AI tools",
    "Travel & Expense": "Approvals, receipts, lodging, meals, non-reimbursable costs",
}

st.set_page_config(page_title="Enterprise Policy RAG", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; max-width: 1180px; }
    [data-testid="stSidebar"] { background: #0f172a; }
    [data-testid="stSidebar"] * { color: #e5e7eb; }
    .hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid #dbe3ef;
        border-radius: 10px;
        background: linear-gradient(135deg, #ffffff 0%, #eef6ff 100%);
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0 0 .35rem 0; color: #0f172a; font-size: 2rem; }
    .hero p { margin: 0; color: #334155; font-size: 1rem; }
    .capability-box {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: .85rem 1rem;
        background: #ffffff;
        min-height: 112px;
    }
    .capability-box b { color: #0f172a; }
    .muted { color: #64748b; font-size: .92rem; }
    .source-card {
        border-left: 4px solid #2563eb;
        background: #f8fafc;
        padding: .75rem .9rem;
        border-radius: 6px;
        margin-bottom: .65rem;
    }
    .small-label { color: #475569; font-size: .82rem; text-transform: uppercase; letter-spacing: .04em; }
    </style>
    """,
    unsafe_allow_html=True,
)

pdf_count = len(list(SAMPLE_DOCS.glob("*.pdf"))) if SAMPLE_DOCS.exists() else 0


@st.cache_resource(show_spinner=False)
def ensure_default_index() -> str:
    settings = get_settings()
    store = ChromaVectorStore(settings)
    index_is_empty = store.is_empty()
    store.close()

    if pdf_count and index_is_empty:
        result = ingest_directory(SAMPLE_DOCS, reset=True)
        return f"Ready: indexed {result.files_processed} PDFs into {result.chunks_created} chunks."
    return "Ready: policy index loaded."


index_status = ensure_default_index()

with st.sidebar:
    st.subheader("Knowledge Base")
    st.metric("Policy PDFs", pdf_count)
    st.caption("Vector DB: Qdrant local mode")
    st.caption("LLM: Groq")
    st.caption(index_status)

    uploaded_files = st.file_uploader(
        "Upload more policy documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        SAMPLE_DOCS.mkdir(parents=True, exist_ok=True)
        for uploaded in uploaded_files:
            (SAMPLE_DOCS / uploaded.name).write_bytes(uploaded.getbuffer())
        st.success(f"Saved {len(uploaded_files)} file(s). Rebuild the index before asking about them.")

    if st.button("Rebuild Vector Index", type="primary", use_container_width=True):
        with st.spinner("Chunking documents, embedding text, and rebuilding Qdrant..."):
            result = ingest_directory(SAMPLE_DOCS, reset=True)
        st.success(f"Indexed {result.files_processed} files into {result.chunks_created} chunks.")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Documents")
    for path in sorted(SAMPLE_DOCS.glob("*.pdf")):
        st.caption(path.name.replace("_", " ").replace(".pdf", "").title())

st.markdown(
    """
    <div class="hero">
      <h1>Enterprise Policy Intelligence RAG</h1>
      <p>Ask grounded questions across HR, safety, security, workplace conduct, travel, and expense policies. Answers are generated with Groq and backed by retrieved policy evidence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("Indexed domains", "5")
metric_cols[1].metric("Sample PDFs", str(pdf_count))
metric_cols[2].metric("Retrieval", "Hybrid")
metric_cols[3].metric("Citations", "Enabled")

tab_chat, tab_capabilities, tab_documents = st.tabs(["Ask", "What You Can Ask", "Policy Library"])

with tab_capabilities:
    st.subheader("This assistant can answer questions about")
    cols = st.columns(2)
    for idx, item in enumerate(CAPABILITIES):
        with cols[idx % 2]:
            st.markdown(f"<div class='capability-box'><b>{item.split(',')[0]}</b><br><span class='muted'>{item}</span></div>", unsafe_allow_html=True)
            st.write("")

    st.subheader("Example questions")
    for question in SUGGESTED_QUESTIONS:
        st.code(question, language=None)

with tab_documents:
    st.subheader("Included policy areas")
    for area, description in POLICY_AREAS.items():
        st.markdown(f"**{area}**  ")
        st.caption(description)
    st.divider()
    st.subheader("Indexed PDF files")
    for path in sorted(SAMPLE_DOCS.glob("*.pdf")):
        st.write(f"- {path.name}")

with tab_chat:
    st.subheader("Ask a policy question")
    st.caption("Try asking about approvals, deadlines, reporting obligations, eligibility, limits, or required employee actions.")

    selected_question = st.selectbox("Quick question", ["Choose an example..."] + SUGGESTED_QUESTIONS)
    col_a, col_b = st.columns([1, 5])
    with col_a:
        use_example = st.button("Ask", use_container_width=True, disabled=selected_question == "Choose an example...")
    with col_b:
        st.markdown("<span class='muted'>The assistant answers only from indexed documents and shows retrieved evidence.</span>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    prompt = None
    if use_example and selected_question != "Choose an example...":
        prompt = selected_question

    typed_question = st.chat_input("Ask about leave, safety, vacation, rules, security, travel, or expenses")
    if typed_question:
        prompt = typed_question

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving policy evidence and generating a grounded answer..."):
                answer, chunks = answer_question(prompt)
            st.markdown(answer)
            with st.expander("Retrieved evidence", expanded=True):
                for chunk in chunks:
                    page = f"page {chunk.page}" if chunk.page else "document"
                    st.markdown(
                        f"<div class='source-card'><span class='small-label'>{chunk.source} - {page} - relevance {chunk.score:.3f}</span><br>{chunk.text}</div>",
                        unsafe_allow_html=True,
                    )
        st.session_state.messages.append({"role": "assistant", "content": answer})
