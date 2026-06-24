import subprocess
import sys

# 云端自动补全缺失依赖
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "langchain==0.3.30",
    "langchain-community==0.3.31",
    "langchain-openai==0.3.35",
    "langchain-text-splitters==0.3.11",
    "faiss-cpu",
    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
])

# RAG智能文档问答机器人
import streamlit as st
from file_processer import read_file
from text_splitter import split_text
from vector_store import VectorStore
from llm_service import generate_answer

# ===== 侧边栏：API Key配置 =====
with st.sidebar:
    st.subheader("API密钥配置")
    DASHSCOPE_API_KEY = st.text_input(
        "通义千问 API Key",
        type="password",
        placeholder="粘贴sk开头的密钥"
    )
    st.caption(
        "本应用需使用通义千问API。请前往[阿里云百炼平台]"
        "(https://bailian.aliyun.com)免费申请API Key。"
    )

# ===== 校验密钥是否填写 =====
if not DASHSCOPE_API_KEY:
    st.warning("请在左侧侧边栏输入你的通义千问API密钥后，才能使用本系统！")
    st.stop()

# ===== 初始化向量库（使用用户输入的Key） =====
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore(api_key=DASHSCOPE_API_KEY)
vector_store = st.session_state.vector_store

# ===== 页面标题 =====
st.title("智能文档问答机器人")

# ===== 文件上传逻辑 =====
upload_file = st.file_uploader("上传文件", type=["txt", "pdf"])
if upload_file is not None:
    st.write(f"您已上传文件：{upload_file.name}")
    content = read_file(upload_file)
    chunks = split_text(content)
    num_chunks = vector_store.add_documents(chunks)
    if num_chunks == 0:
        st.warning("上传的文档内容为空，无法分割。请上传一个有文字内容的文件。")
    else:
        st.success(f"已处理文件，共分割为{num_chunks}块，已存入向量库。")

# ===== 提问与检索 =====
st.divider()
st.subheader("提问")
question = st.text_area("请输入你的问题：", height=150)
if st.button("搜索") and question:
    with st.spinner("正在检索..."):
        results_docs = vector_store.search(question, top_k=3)
    if results_docs:
        context = "\n\n".join(results_docs)
        with st.spinner("AI正在生成回答..."):
            ai_answer = generate_answer(question, context, api_key=DASHSCOPE_API_KEY)
        st.write("检索到的相关内容：")
        for i, doc in enumerate(results_docs):
            st.markdown(f"**相关段落{i + 1}**")
            st.write(doc)
            st.divider()
        st.subheader("AI的回答")
        st.write(ai_answer)
    else:
        st.warning("没有在文档中找到相关内容，请尝试换个问法或上传其他文档。")