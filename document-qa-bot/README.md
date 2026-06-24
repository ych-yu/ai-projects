# 智能文档问答机器人（RAG）

基于 **RAG（检索增强生成）** 技术开发的智能文档问答系统。用户上传 PDF 或 TXT 文档后，系统自动解析、分块、向量化存储。用户提问时，从文档中检索最相关的内容，结合通义千问大模型生成精准回答，并展示引用来源。

**🔗 公网访问链接**：[点击试用](https://ai-projects-gujsk3bdmn9bshujusbig2.streamlit.app/)

---

## 功能特性

- 📂 **多格式支持**：支持上传 TXT、PDF 文件
- 🌐 **多语言兼容**：纯中文、纯英文、中英混合文档均可处理
- ✂️ **语义分块**：基于 LangChain 的递归分割器，智能识别段落边界
- 🔍 **语义检索**：基于 ChromaDB 向量数据库，按语义相似度检索
- 🤖 **大模型问答**：接入通义千问 API，基于文档内容生成回答
- 📚 **引用溯源**：展示回答引用的原始文本段落
- 🧱 **模块化架构**：文件处理、文本分割、向量存储、大模型调用分离为独立模块

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python |
| 网页框架 | Streamlit |
| 文本分割 | LangChain RecursiveCharacterTextSplitter |
| 向量存储 | ChromaDB |
| 嵌入模型 | 阿里云百炼 text-embedding-v1 |
| 大模型 | 通义千问 qwen-plus |
| 部署平台 | Streamlit Cloud |

---

## 项目结构
document-qa-bot/
├── app.py # 主程序，页面渲染与流程调度
├── file_processor.py # 文件处理模块（TXT/PDF 解析）
├── text_splitter.py # 文本分割模块（段落级智能切分）
├── vector_store.py # 向量存储与检索模块（ChromaDB 封装）
├── llm_service.py # 大模型调用模块（通义千问 API 封装）
├── requirements.txt # 依赖列表
└── README.md # 项目文档

---

## 安装与使用

### 1. 克隆仓库

```bash
git clone https://github.com/ych-yu/ai-projects.git
cd ai-projects/document-qa-bot
