import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    def __init__(self, api_key, collection_name="my_docs"):
        self.embedding = OpenAIEmbeddings(
            openai_api_key=api_key,
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="text-embedding-v1"
        )
        self.persist_path = f"./{collection_name}_chroma_db"
        self.db = Chroma(
            persist_directory=self.persist_path,
            embedding_function=self.embedding,
            collection_name=collection_name
        )

    def _clear_all(self):
        all_docs = self.db.get()
        ids = all_docs["ids"]
        if ids:
            self.db.delete(ids=ids)

    def add_documents(self, chunks):
        self._clear_all()
        if len(chunks) == 0:
            return 0
        self.db.add_texts(texts=chunks)
        self.db.persist()
        return len(chunks)

    def search(self, question, top_k=3):
        res = self.db.similarity_search(question, k=top_k)
        return [doc.page_content for doc in res]

    def count(self):
        return len(self.db.get()["documents"])