import numpy as np
import requests
import json
import os

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
        self.client = chromadb.PersistentClient(path="./my_chroma_db")
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
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.ef,
                metadata={"hnsw:space": "cosine"}
            )

    def _clear_all(self):
        """清空集合所有数据"""
        try:
            all_data = self.collection.get()
            all_ids = all_data["ids"]
            if len(all_ids) > 0:
                self.collection.delete(ids=all_ids)
        except Exception:
            self.client.delete_collection(self.collection_name)
            self._get_or_create_collection()

    def add_documents(self, chunks):
        """批量存入文本块（分批，每批最多25个）"""
        self._clear_all()
        batch_size = 25
        total = 0
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
        """语义检索"""
        results = self.collection.query(
            query_texts=[question],
            n_results=top_k
        )
        return results["documents"][0] if results["documents"][0] else []

    def count(self):
        """返回当前集合中存储的文本块数量"""
        return self.collection.count()
class VectorStore:
    """轻量级向量存储，使用numpy进行余弦相似度计算，不依赖chromadb"""

    def __init__(self, api_key, storage_path="./vector_data.json"):
        self.api_key = api_key
        self.storage_path = storage_path
        self.documents = []
        self.embeddings = []
        self._load_from_disk()

    def _embed(self, texts):
        """调用阿里云Embedding API"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-v1",
            "input": {"texts": texts}
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            return [item["embedding"] for item in resp_json["output"]["embeddings"]]
        else:
            raise Exception(f"Embedding API调用失败: {response.status_code} {response.text}")

    def _cosine_similarity(self, vec1, vec2):
        """计算两个向量的余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def _save_to_disk(self):
        """持久化到本地JSON文件"""
        data = {
            "documents": self.documents,
            "embeddings": [emb.tolist() if isinstance(emb, np.ndarray) else emb for emb in self.embeddings]
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def _load_from_disk(self):
        """从本地JSON文件加载数据"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.documents = data.get("documents", [])
                self.embeddings = [np.array(emb) for emb in data.get("embeddings", [])]

    def add_documents(self, chunks):
        """批量存入文本块"""
        self.documents = []
        self.embeddings = []
        batch_size = 25
        total = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            batch_embeddings = self._embed(batch)
            self.documents.extend(batch)
            self.embeddings.extend([np.array(emb) for emb in batch_embeddings])
            total += len(batch)
        self._save_to_disk()
        return total

    def search(self, question, top_k=3):
        """语义检索"""
        if not self.embeddings:
            return []
        question_embedding = np.array(self._embed([question])[0])
        similarities = []
        for i, emb in enumerate(self.embeddings):
            sim = self._cosine_similarity(question_embedding, emb)
            similarities.append((i, sim))
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:top_k]
        return [self.documents[i] for i, _ in top_results]

    def count(self):
        return len(self.documents)