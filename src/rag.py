#!/usr/bin/env python3
"""
RAG 系统 - 检索增强生成
支持多种向量数据库
"""
import json
import os
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests


# ============== 基础类 ==============
@dataclass
class Document:
    """文档"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class VectorDB(ABC):
    """向量数据库基类"""

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """添加文档"""
        pass

    @abstractmethod
    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        """相似度搜索"""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """删除集合"""
        pass


# ============== ChromaDB 实现 ==============
class ChromaDB(VectorDB):
    """ChromaDB 向量数据库"""

    def __init__(self, collection_name: str = "xiaohongshu"):
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            print("⚠️ 未安装 chromadb，请运行: pip install chromadb")
            self.client = None
            return

        self.client = chromadb.Client(Settings(
            persist_directory="./data/chroma",
            anonymized_telemetry=False
        ))
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(self, documents: List[Document]) -> None:
        if not self.client:
            return

        ids = [d.id for d in documents]
        contents = [d.content for d in documents]
        metadatas = [d.metadata for d in documents]

        # 生成 embedding (简化版)
        embeddings = [self._simple_embedding(d.content) for d in documents]

        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        if not self.client:
            return []

        query_embedding = self._simple_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = []
        if results["documents"]:
            for i, content in enumerate(results["documents"][0]):
                doc = Document(
                    id=results["ids"][0][i],
                    content=content,
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {}
                )
                documents.append(doc)

        return documents

    def delete_collection(self) -> None:
        if self.client:
            self.client.delete_collection(self.collection_name)

    def _simple_embedding(self, text: str) -> List[float]:
        """简单的 embedding (使用 hash)"""
        # 实际应该使用真正的 embedding 模型
        hash_val = hashlib.md5(text.encode()).digest()
        return [float(b) / 255.0 for b in hash_val[:32]]


# ============== 内存实现 (无需外部依赖) ==============
class InMemoryVectorDB(VectorDB):
    """内存向量数据库"""

    def __init__(self):
        self.documents: List[Document] = []

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)

    def similarity_search(self, query: str, top_k: int = 5) -> List[Document]:
        # 简单的关键词匹配
        query_words = set(query.lower().split())
        scored = []

        for doc in self.documents:
            doc_words = set(doc.content.lower().split())
            # 计算交集
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scored.append((overlap, doc))

        # 排序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def delete_collection(self) -> None:
        self.documents = []


# ============== RAG 系统 ==============
class RAGSystem:
    """RAG 检索增强系统"""

    def __init__(
        self,
        vector_db: VectorDB = None,
        embedding_model: str = "text-embedding-3-small"
    ):
        self.vector_db = vector_db or InMemoryVectorDB()
        self.embedding_model = embedding_model
        self.knowledge_base: List[Document] = []

    def add_knowledge(self, content: str, metadata: Dict[str, Any]) -> None:
        """添加知识"""
        doc_id = hashlib.md5(content.encode()).hexdigest()
        doc = Document(
            id=doc_id,
            content=content,
            metadata=metadata
        )
        self.knowledge_base.append(doc)
        self.vector_db.add_documents([doc])

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """检索相关知识"""
        return self.vector_db.similarity_search(query, top_k)

    def generate(
        self,
        query: str,
        llm_adapter,
        system_prompt: str = None,
        context: List[Document] = None
    ) -> str:
        """生成回答"""
        # 检索相关知识
        if context is None:
            context = self.retrieve(query)

        # 构建上下文
        context_text = "\n\n".join([
            f"[{i+1}] {doc.content}"
            for i, doc in enumerate(context)
        ])

        # 构建提示词
        if system_prompt is None:
            system_prompt = """你是一个专业的小红书运营助手。
根据以下知识库内容回答用户问题。

知识库：
{context}

请根据知识库内容回答问题。如果知识库中没有相关信息，请如实说明。"""

        user_prompt = f"""用户问题：{query}

请根据上述知识库内容回答。"""

        messages = [
            {"role": "system", "content": system_prompt.format(context=context_text)},
            {"role": "user", "content": user_prompt}
        ]

        # 调用 LLM
        return llm_adapter.chat(messages)

    def load_from_json(self, file_path: str) -> None:
        """从 JSON 文件加载知识"""
        if not os.path.exists(file_path):
            print(f"⚠️ 文件不存在: {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            if content:
                self.add_knowledge(content, metadata)

        print(f"✅ 已加载 {len(data)} 条知识")

    def save_to_json(self, file_path: str) -> None:
        """保存知识到 JSON 文件"""
        data = [
            {"content": doc.content, "metadata": doc.metadata}
            for doc in self.knowledge_base
        ]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 已保存 {len(data)} 条知识到 {file_path}")


# ============== 内置知识库 ==============
def get_default_knowledge() -> List[Dict[str, Any]]:
    """获取默认知识库"""
    return [
        {
            "content": "小红书标题技巧：使用数字+悬念+关键词，如'5个方法让你的笔记爆火'",
            "metadata": {"type": "title", "category": "运营"}
        },
        {
            "content": "小红书热门时间段：早上7-9点，中午12-14点，晚上20-24点",
            "metadata": {"type": "timing", "category": "运营"}
        },
        {
            "content": "小红书标签选择：选择1-2个泛标签+2-3个精准标签",
            "metadata": {"type": "tags", "category": "内容"}
        },
        {
            "content": "AI Agent 是企业的数字化员工，可以自动化处理重复性工作",
            "metadata": {"type": "concept", "category": "AI"}
        },
        {
            "content": "企业搭建 AI Agent 的5个核心要素：明确场景、选择能力、构建知识库、设计工作流、持续优化",
            "metadata": {"type": "framework", "category": "AI"}
        },
        {
            "content": "高质量小红书内容的3个要素：利他性、真实性、情感共鸣",
            "metadata": {"type": "quality", "category": "内容"}
        },
    ]


# ============== 测试 ==============
if __name__ == "__main__":
    print("🧪 测试 RAG 系统")
    print("=" * 50)

    # 创建 RAG 系统
    rag = RAGSystem(vector_db=InMemoryVectorDB())

    # 添加内置知识
    print("\n[1] 添加知识库...")
    for item in get_default_knowledge():
        rag.add_knowledge(item["content"], item["metadata"])
    print(f"   已添加 {len(rag.knowledge_base)} 条知识")

    # 测试检索
    print("\n[2] 测试检索...")
    results = rag.retrieve("如何写小红书标题")
    print(f"   找到 {len(results)} 条相关内容")
    for i, doc in enumerate(results):
        print(f"   {i+1}. {doc.content[:50]}...")

    # 测试生成 (模拟)
    print("\n[3] RAG 系统测试完成")

    print("\n✅ RAG 系统就绪")
