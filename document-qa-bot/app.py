# 导入包库
import streamlit as st
from file_processer import read_file
from text_splitter import split_text
from vector_store import VectorStore
from llm_service import generate_answer

# ========== 新增：侧边栏输入API密钥，完全抛弃st.secrets ==========
with st.sidebar:
    st.subheader("通义千问API配置")
    DASHSCOPE_API_KEY = st.text_input("DASHSCOPE_API_KEY", type="password", placeholder="粘贴sk开头密钥")

# 校验密钥是否填写，为空直接停止页面
if not DASHSCOPE_API_KEY:
    st.warning("⚠️ 请在左侧侧边栏输入通义千问API密钥后，才能使用文档问答功能！")
    st.stop()
# ==============================================================

# 初始化向量库（用st.session_state确保只初始化一次）
if "vector_store" not in st.session_state:
    # 不再读取st.secrets，传入页面输入的密钥
    st.session_state.vector_store = VectorStore(api_key=DASHSCOPE_API_KEY)
vector_store = st.session_state.vector_store

# 页面标题
st.title("智能文档问答机器人")

# 文件上传逻辑
upload_file = st.file_uploader("上传文件", type=["txt", "pdf"])
if upload_file is not None:
    st.write(f"您已上传文件：{upload_file.name}")
    content = read_file(upload_file)
    chunks = split_text(content)
    # 批量存入向量库
    num_chunks = vector_store.add_documents(chunks)
    if num_chunks == 0:
        st.warning("上传的文档内容为空，无法分割。请上传一个有文字内容的文件。")
    else:
        st.success(f"已处理文件，共分割为{num_chunks}块，已存入向量库。")

# 提问与检索
st.divider()
st.subheader("提问")
question = st.text_area("请输入你的问题：", height=150)

if st.button("搜索") and question:
    with st.spinner("正在检索..."):
        results_docs = vector_store.search(question, top_k=3)
    if results_docs:
        context = "\n\n".join(results_docs)
        with st.spinner("AI正在生成回答..."):
            # 传入页面输入的密钥
            ai_answer = generate_answer(question, context, api_key=DASHSCOPE_API_KEY)
        # 展示检索到的原文
        st.write("检索到的相关内容：")
        for i, doc in enumerate(results_docs):
            st.markdown(f"**相关段落{i + 1}**")
            st.write(doc)
            st.divider()
        # 展示AI回答
        st.subheader("AI的回答")
        st.write(ai_answer)
    else:
        st.warning("没有在文档中找到相关内容，请尝试换个问法或上传其他文档。")