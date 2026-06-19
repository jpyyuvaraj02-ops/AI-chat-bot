import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

# Load environment variables
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="AI Knowledge Assistant", page_icon="🤖")

# Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error(
        "Missing GROQ_API_KEY. Set this variable in your environment or in a .env file before running the app."
    )
    st.stop()

# Groq client
client = Groq(api_key=groq_api_key)
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1 {
    color: #00E5FF;
}

.stChatMessage {
    border-radius: 15px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)
st.title("🤖 AI Knowledge Assistant")
st.markdown("""
Ask questions about AI, Programming, Data Science, Technology and General Knowledge.
""")
st.info(
    "👋 Welcome! Ask me anything about AI, Programming, Data Science, Technology and General Knowledge."
)
st.sidebar.title("About")
st.sidebar.write("Ask questions on technology, AI, programming, data science, and general knowledge.")
st.write(os.path.exists("robot_ai.jpg.png"))
image_path = "robot_ai.jpg.png"
if os.path.exists(image_path):
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image( "robot_ai.jpg.png", width=400)
    except Exception:
        st.warning("Unable to load local image. Using fallback image.")
        st.image(
            "https://images.unsplash.com/photo-1677442136019-21780ecad995",
            use_container_width=True,
        )
else:
    st.image(
        "https://images.unsplash.com/photo-1677442136019-21780ecad995",
        use_container_width=True,
    )
st.sidebar.title("⚡ AI Assistant")

st.sidebar.success("🟢 Online")

st.sidebar.markdown("---")

st.sidebar.subheader("💡 Try Asking")

st.sidebar.write("🤖 What is Generative AI?")
st.sidebar.write("🧠 Explain Machine Learning")
st.sidebar.write("📊 What is Data Science?")
st.sidebar.write("🔒 What is Cyber Security?")
st.sidebar.write("☁️ Explain Cloud Computing")
st.sidebar.write("💻 Why use GitHub?")
st.sidebar.markdown("---")

st.sidebar.subheader("🛠 Tech Stack")

st.sidebar.write("⚡ Groq")
st.sidebar.write("🦜 LangChain")
st.sidebar.write("🔍 FAISS")
st.sidebar.write("🎨 Streamlit")
# Load and cache vector database
# -----------------------------
@st.cache_resource
def load_vectorstore():
    # Use absolute path to handle different working directories (local vs Streamlit Cloud)
    data_path = os.path.join(os.path.dirname(__file__), "data.txt")
    if not os.path.exists(data_path):
        st.error("data.txt file not found at {}".format(data_path))
        st.stop()

    documents = []

    try:
        text_loader = TextLoader(data_path)
        documents.extend(text_loader.load())
    except Exception as exc:
        st.error(f"Failed to load data.txt: {exc}")
        st.stop()

    splitter = CharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings()

    db = FAISS.from_documents(docs, embeddings)

    return db.as_retriever()
    

retriever = load_vectorstore()

# -----------------------------
# Chat history
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# User input
# -----------------------------
prompt = st.chat_input("💬 Ask your question here...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    docs = retriever.invoke(prompt)
    context = "\n\n".join([d.page_content for d in docs[:3]])
    full_prompt = f"""
You are an AI Knowledge Assistant.

Never mention XYZ Engineering College or any college.

Answer questions about AI, Programming, Technology, Data Science and General Knowledge.

Use the context when relevant.
If context is not enough, use your general knowledge.

Context:
{context}

Question:
{prompt}

Answer:
"""
    messages = []

    for m in st.session_state.messages:
        messages.append({
            "role": m["role"],
            "content": m["content"]
        })

    messages.append({
        "role": "user",
        "content": full_prompt
    })
    chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

    answer = chat.choices[0].message.content

    st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    with st.chat_message("assistant"):
            st.write(answer)
        