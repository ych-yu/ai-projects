import chromadb
from http import HTTPStatus
from dashscope import TextEmbedding

class VectorStore:
    def __init__(self, api_key, collection_name="my_docs"):
        self.api_key = api_key
        self.client = chromadb.PersistentClient(path="./my_chroma_db")
        self.collection_name = collection_name
        self._init_collection()

    def _init_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def _embed(self, texts):
        """使用dashscope SDK调用Embedding API"""
        resp = TextEmbedding.call(
            model="text-embedding-v1",
            api_key=self.api_key,
            texts=texts
        )
        if resp.status_code == HTTPStatus.OK:
            return [item["embedding"] for item in resp.output["embeddings"]]
        else:
            raise Exception(f"Embedding API调用失败: {resp.code} {resp.message}")

    def add_documents(self, chunks):
        self._init_collection()
        batch_size = 25
        total = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            ids = [f"chunk_{start + i}" for i in range(len(batch))]
            embeddings = self._embed(batch)
            self.collection.add(
                documents=batch,
                embeddings=embeddings,
                ids=ids
            )
            total += len(batch)
        return total

    def search(self, question, top_k=3):
        question_embedding = self._embed([question])[0]
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        return results["documents"][0] if results["documents"][0] else []

    def count(self):
        return self.collection.count()