import os
from dotenv import load_dotenv

# 1. Load API Key from .env
load_dotenv(os.path.join(os.path.dirname(__file__), 'env', '.env'))

# Check if Key is loaded successfully
if not os.getenv("GOOGLE_API_KEY") or not os.getenv("OPENAI_API_KEY"):
    print("Error: Please check the .env file to ensure GOOGLE_API_KEY and OPENAI_API_KEY are filled in correctly!")
    exit()

# --- Import LangChain Components ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 2. Configure Model (Hybrid Architecture)

# Chat Model: Use Google Gemini 2.5 Flash-Lite
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    temperature=0
)

# Embedding Model: Use OpenAI text-embedding-3-small
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 3. Load and Process Data - For three language versions
def load_and_build_vectorstore(language, folder_path):
    """
    Load documents and build vector database for the specified language
    """
    print(f"\nScanning all .md files in the {folder_path} folder...")
    
    try:
        loader = DirectoryLoader(
            path=folder_path, 
            glob="*.md", 
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        
        docs = loader.load()
        docs = loader.load()
        print(f"{language} version: Successfully loaded {len(docs)} files.")

        # Text Splitting (Chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        print(f"Splitting completed, generated {len(splits)} document chunks.")
        print(f"Building vector database for {language} version...")

        # Build vector database
        vectorstore = FAISS.from_documents(splits, embeddings)
        vectorstore.save_local(f"./rag_vectorstore_{language}")
        print(f"Vector database for {language} version saved!")
        
        return vectorstore
        
    except Exception as e:
        print(f"Error reading {language} version files: {e}")
        return None

# Load data for three language versions
languages = {
    "cn": "./rag_docs/cn",
    "en": "./rag_docs/en",
    "jp": "./rag_docs/jp"
}

vectorstores = {}
for lang_code, folder_path in languages.items():
    vectorstore_path = f"./rag_vectorstore_{lang_code}"
    
    if os.path.exists(vectorstore_path):
        print(f"Loading existing {lang_code} vectorstore...")
        try:
            vectorstores[lang_code] = FAISS.load_local(
                vectorstore_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            print(f"Loaded {lang_code} vectorstore from disk.")
        except Exception as e:
            print(f"Failed to load existing {lang_code} vectorstore: {e}")
            print(f"Rebuilding {lang_code} vectorstore...")
            if os.path.exists(folder_path):
                vectorstores[lang_code] = load_and_build_vectorstore(lang_code, folder_path)
    elif os.path.exists(folder_path):
        vectorstores[lang_code] = load_and_build_vectorstore(lang_code, folder_path)
    else:
        print(f"Warning: {folder_path} folder does not exist, skipping {lang_code} version")

if not vectorstores:
    print("Error: Failed to load data for any language version!")
    exit()

print(f"\nSuccessfully loaded {len(vectorstores)} language version databases")

# 5. Define RAG Prompt Templates
templates = {
    "cn": """
你是一个精通 MBTI 人格理论的专家助手。
请基于下面的【背景信息】回答用户的【问题】。
如果背景信息里没有答案，请诚实地说不知道，不要编造。

【背景信息】：
{context}

【用户问题】：
{question}
""",
    "en": """
You are an expert assistant proficient in MBTI personality theory.
Please answer the user's【question】based on the following【background information】.
If the background information does not contain the answer, please honestly say you don't know, don't make it up.

【Background Information】:
{context}

【User Question】:
{question}
""",
    "jp": """
あなたはMBTI人格理論に精通した専門家アシスタントです。
以下の【背景情報】に基づいて、ユーザーの【質問】に答えてください。
背景情報に答えがない場合は、正直に知らないと言ってください。作り話をしないでください。

【背景情報】：
{context}

【ユーザーの質問】：
{question}
"""
}

prompts = {lang: ChatPromptTemplate.from_template(template) for lang, template in templates.items()}

# 6. Build RAG chains for three language versions
rag_chains = {}
for lang_code, vectorstore in vectorstores.items():
    retriever = vectorstore.as_retriever()
    rag_chains[lang_code] = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompts[lang_code]
        | llm
        | StrOutputParser()
    )
    print(f"{lang_code.upper()} RAG chain established")

# --- Interactive Q&A Loop ---
if __name__ == "__main__":
    print("\n=== MBTI Intelligent Assistant Ready ===")
    print("Supported languages: CN (Chinese), EN (English), JP (Japanese)")
    print("Enter 'exit' to quit\n")

    current_language = "cn"  # Default Chinese

    while True:
        lang_hint = f"[{current_language.upper()}]"
        user_input = input(f"\n{lang_hint} Please ask (or enter 'lang' to switch language): ")
        
        # Handle language switching
        if user_input.lower() == "lang":
            print("\nChoose language: CN (Chinese) | EN (English) | JP (Japanese)")
            lang_choice = input("Enter language code: ").lower()
            if lang_choice in rag_chains:
                current_language = lang_choice
                print(f"Switched to {lang_choice.upper()} version")
            else:
                print(f"Unsupported language code: {lang_choice}")
            continue
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        
        if not user_input.strip():
            continue

        print("Thinking...", end="", flush=True)
        try:
            response = rag_chains[current_language].invoke(user_input)
            # Clear "Thinking..." and print answer
            print(f"\r{' ' * 20}\r", end="") 
            print(f"Answer: {response}")
        except Exception as e:
            print(f"\nCall Error: {e}")

# --- End of RAG Bot ---