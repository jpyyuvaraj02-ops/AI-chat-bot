import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import groq
from groq import Groq

# Load environment variables
load_dotenv()
from tavily import TavilyClient
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))



# Streamlit page setup
st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="🤖",
    layout="centered"
)
# Initialize Tavily client

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
    border-radius: 10px;
    padding: 8px;
}

a {
    word-break: break-all;
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

st.sidebar.title("⚡ AI Assistant")

st.sidebar.success("🟢 Online")
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

with st.sidebar.expander("💡 Try Asking"):
    st.write("🤖 What is Generative AI?")
    st.write("🧠 Explain Machine Learning")
    st.write("📊 What is Data Science?")
    st.write("🔒 What is Cyber Security?")
st.sidebar.markdown("---")

    
# Load and cache vector database
# -----------------------------
def search_web(query):
    try:
        result = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        web_results = []
        sources = []

        for r in result.get("results", []):
            title = r.get("title", "")
            content = r.get("content", "")

            web_results.append(
                f"Title: {title}\nContent: {content}"
            )

            sources.append(r.get("url", ""))

        return "\n\n".join(web_results), sources
    except Exception as e:
        st.error(f"Web search failed: {e}")
        return "", []

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
    prompt_lower = prompt.lower().strip()
    st.session_state.messages.append({
    "role": "user",
    "content": prompt
})
    with st.chat_message("user"):
     st.write(prompt)
    greetings = [
        "hi", "hello", "hey", "hii",
        "good morning", "good afternoon",
        "good evening", "how are you"
    ]

    is_greeting = any(
        prompt_lower.startswith(g)
        for g in greetings
    )
    casual_keywords = [
        "hi",
        "hello",
        "hii",
        "hey",
        "how are you",
        "tell me about yourself",
        "tell me about your self",
        "who are you",
        "who made you",
        "who developed you",
        "owner",
        "creator",
        "developer",
        "thank you",
        "thanks",
        "ok",
        "okay",
        "super"
    ]

    is_casual = any(
        word in prompt_lower
        for word in casual_keywords
    )
    owner_keywords = [
    "who made you",
    "who created you",
    "your owner",
    "tell me about yourself",
    "tell me about your self",
    "introduce yourself",
    "who developed you",
    "who are you"


]

    if any(k in prompt_lower for k in owner_keywords):

        answer = """
    Hello! 👋

    I am an AI Knowledge Assistant developed by Yuvaraj.

    I can help with:
    • Artificial Intelligence
    • Machine Learning
    • Data Science
    • Programming
    • Technology
    • General Knowledge

    My goal is to provide accurate answers and learning support.
    """

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        st.stop()

    tech_keywords = [
        "python", "java", "c", "c++", "javascript",
        "html", "css", "sql",
        "programming", "coding", "developer",
        "ai", "artificial intelligence",
        "machine learning", "deep learning",
        "data science", "database",
        "cloud", "cyber security",
        "algorithm", "github"
    ]
    
    is_tech = any(
        keyword in prompt_lower
        for keyword in tech_keywords
    )
    current_affairs_keywords = [
        "pm",
        "prime minister",
        "cm",
        "chief minister",
        "president",
        "governor",
        "minister",
        "election",
        "ipl",
        "world cup",
        "winner",
        "score",
        "today",
        "latest",
        "current"
    ]

    is_current_affair = any(
        word in prompt_lower
        for word in current_affairs_keywords
    )
    
    # General Knowledge = NOT technical and NOT casual
    need_web = (
    is_current_affair
    or (not is_tech and not is_casual)
)
    if is_casual:
        web_context = ""
        sources = []
    else:
        if need_web:
            web_context, sources = search_web(prompt)
            
        else:
            web_context = ""
            sources = []
    
    docs = retriever.invoke(prompt)
    rag_context = "\n\n".join([d.page_content for d in docs[:3]])

    context = f"""
RAG Knowledge:
{rag_context}

Latest Web Information:
{web_context}
"""
    full_prompt = f"""
You are AI Knowledge Assistant.

Identity:
- Your name is AI Knowledge Assistant.
- You were created by Yuvaraj.
- If someone asks "who made you", "who is your owner", "who developed you",
  answer: "I was developed by Yuvaraj."
- Do not claim to be ChatGPT, OpenAI, Groq, LangChain or any other company.
- Do not describe internal technologies unless explicitly asked.
- Keep self-introduction under 5 lines.

Rules:
- For greetings, reply naturally in 1-2 sentences.
- For casual chat, keep answers short.
- For technical questions, use RAG Knowledge first and explain in detail.
- For general knowledge, use Web Information when available.

For technical questions:
- Use RAG Knowledge first.
- Give detailed explanation.
- Minimum 300 words.
- Explain step by step.
- Use headings.
- Use bullet points.
- Give examples.
- If learning roadmap is asked, provide beginner to advanced roadmap.
IMPORTANT:

- If Web Information exists, ignore RAG Knowledge for current affairs.
- Current affairs include PM, CM, President, Elections, Sports results and Government positions.
- Never combine Web Information and RAG Knowledge.
- Give only one final answer.
- Do not say "According to RAG Knowledge".
- Do not mention conflicting information.
Rules:
- For political positions, PM, CM, President, Ministers and current affairs,
  ALWAYS use Web Information.
- Ignore RAG Knowledge if it conflicts with Web Information.
- Web Information has higher priority than RAG Knowledge.
  

RAG Knowledge:
{rag_context}

Web Information:
{web_context}

Question:
{prompt}

Answer:
"""
    messages = [
        {
            "role": m["role"],
            "content": m["content"]
        }
        for m in st.session_state.messages[-10:]
    ]

    messages.append({
        "role": "user",
        "content": full_prompt
    })
    with st.spinner("🤖 AI is thinking..."):
        rate_limited = False
        try:
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )

            answer = chat.choices[0].message.content

        except groq.RateLimitError as e:
            # Handle Groq rate limit gracefully and fallback to RAG-only answer
            rate_limited = True
            st.error("Groq rate limit reached: using RAG-only fallback. Please try again later or upgrade your Groq plan.")
            if need_web:
                answer = (
                    "I'm temporarily unable to perform web searches due to API rate limits. "
                    "Here's what I can share from my internal (RAG) knowledge:\n\n" + rag_context
                )
            else:
                answer = (
                    "I'm temporarily unable to reach the web-model due to rate limits. "
                    "Providing information from my RAG knowledge:\n\n" + rag_context
                )

        except Exception as e:
            st.error(f"API error: {e}")
            answer = "Sorry, I'm temporarily unable to process that request. Please try again later."

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        with st.chat_message("assistant"):
            st.write(answer)

        # Only show web sources when a live web search was used and we're not rate-limited
        if not rate_limited and sources and need_web and not is_casual:
            st.markdown("### 🔗 Sources")
            for s in sources[:3]:
                st.markdown(f"🔗 [{s}]({s})")