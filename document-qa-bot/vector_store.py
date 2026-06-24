import chromadb
from chromadb.utils import embedding_functions

class VectorStore:
    """向量存储与检索模块"""

    def __init__(self, api_key, collection_name="my_docs"):
        self.ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name="text-embedding-v1"
        )
        # 这里替换成带关闭遥测的客户端
        self.client = chromadb.PersistentClient(
            path="./my_chroma_db",
            settings=chromadb.Settings(telemetry=False)
        )
        self.collection_name = collection_name
        self._get_or_create_collection()

    def _get_or_create_collection(self):
        """安全获取/创建集合"""
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.ef
            )
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.ef
            )

    def _clear_all(self):
        """兼容0.4.24 清空集合所有数据"""
        try:
            # 获取全部数据ID
            all_data = self.collection.get()
            all_ids = all_data["ids"]
            if len(all_ids) > 0:
                self.collection.delete(ids=all_ids)
        except Exception:
            # 异常直接删集合重建兜底
            self.client.delete_collection(self.collection_name)
            self._get_or_create_collection()

    def add_documents(self, chunks):
        """
        批量存入文本块（分批处理，每批最多25个，避免超过阿里云API限制）。
        参数：
            chunks: 文本块列表
        返回:
            存入的文本块数量
        """
        # 清空旧数据
        self._clear_all()

        batch_size = 25  # 阿里云embedding API每批最多25条
        total = 0

        # 分批存入
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            ids = [f"chunk_{start + i}" for i in range(len(batch))]
            self.collection.add(
                documents=batch,
                ids=ids
            )
            total += len(batch)

        return total

    def search(self, question, top_k=3):
        self._get_or_create_collection()
        results = self.collection.query(query_texts=[question], n_results=top_k)
        return results["documents"][0] if results["documents"][0] else []

    def count(self):
        self._get_or_create_collection()
        return self.collection.count()
