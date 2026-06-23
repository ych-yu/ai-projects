import chromadb
import requests
import os

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
        """用requests直接调用阿里云Embedding API"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-v1",
            "input": {"texts": texts},
            "parameters": {"text_type": "document"}
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            return [item["embedding"] for item in resp_json["output"]["embeddings"]]
        else:
            raise Exception(f"Embedding API调用失败: {response.status_code} {response.text}")

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
        url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-v1",
            "input": {"texts": [question]},
            "parameters": {"text_type": "query"}
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            raw_emb = resp_json["output"]["embeddings"][0]
            # 确保是一维列表，ChromaDB 不接受嵌套列表
            if isinstance(raw_emb, list) and len(raw_emb) == 1 and isinstance(raw_emb[0], list):
                question_embedding = raw_emb[0]
            else:
                question_embedding = raw_emb
        else:
            return []
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k
        )
        return results["documents"][0] if results["documents"][0] else []

    def count(self):
        return self.collection.count()