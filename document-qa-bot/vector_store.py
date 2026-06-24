import os
# 关闭遥测环境变量，规避无关报错
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# 修正导入路径，适配新版langchain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    """FAISS向量存储模块，替代ChromaDB，无opentelemetry依赖"""
    def __init__(self, api_key, collection_name="my_docs"):
        # 对接阿里云通义千问兼容Embedding接口
        self.embedding = OpenAIEmbeddings(
            openai_api_key=api_key,
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="text-embedding-v1"
        )
        # 本地索引存储文件夹
        self.index_path = f"./{collection_name}_faiss_index"
        self.db = None
        # 加载/初始化空向量库
        self._load_or_create_index()

    def _load_or_create_index(self):
        """读取本地FAISS索引，不存在则创建空库"""
        try:
            self.db = FAISS.load_local(
                folder_path=self.index_path,
                embeddings=self.embedding,
                allow_dangerous_deserialization=True
            )
        except Exception:
            # 无索引文件，初始化空向量库
            self.db = FAISS.from_texts(texts=[], embedding=self.embedding)

    def _clear_all(self):
        """清空所有已存入文档，重建空索引（对应原Chroma清空逻辑）"""
        self.db = FAISS.from_texts([], self.embedding)

    def add_documents(self, chunks):
        """
        存入文本块，上传新文件自动覆盖旧文档
        :param chunks: 文本块列表
        :return: 成功存入的块数量
        """
        # 先清空历史数据，和原项目逻辑保持一致
        self._clear_all()
        if len(chunks) == 0:
            return 0
        # 构建向量索引并保存到本地
        self.db = FAISS.from_texts(chunks, self.embedding)
        self.db.save_local(self.index_path)
        return len(chunks)

    def search(self, question, top_k=3):
        """语义检索，返回top-k相关文本片段"""
        self._load_or_create_index()
        search_result = self.db.similarity_search(query=question, k=top_k)
        # 提取文本内容，格式和原Chroma返回完全一致
        content_list = [doc.page_content for doc in search_result]
        return content_list if content_list else []

    def count(self):
        """获取向量库中文本块总数"""
        self._load_or_create_index()
        return self.db.index.ntotal