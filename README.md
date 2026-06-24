# AI Projects

> 一个记录我从零开始自学Python、通过实战项目掌握AI应用开发能力的成长仓库。

---

## 📂 项目列表

### 🤖 AI周报生成器
**目录**：[weekly_report](./weekly_report)

基于通义千问大模型和Streamlit框架开发的智能办公助手。用户输入零散的工作内容，系统根据岗位类型自动生成格式化周报。

- **技术栈**：Python、Streamlit、阿里云百炼（通义千问 `qwen-plus`）
- **核心功能**：三套岗位专用Prompt（开发/产品/销售）、快速模式+对话模式双交互、对话历史持久化管理、公网部署
- **关键收获**：掌握了Prompt Engineering的调试方法，理解了如何通过强约束词控制AI输出格式，以及用`st.session_state`解决页面状态管理问题

### 🧠 智能文档问答机器人（RAG）
**目录**：[document-qa-bot](./document-qa-bot)

基于RAG（检索增强生成）技术开发的智能文档问答系统。用户上传PDF或TXT文档后，系统自动解析、分块、向量化存储，用户提问时从文档中检索最相关内容，结合大模型生成精准回答，并展示引用来源。

- **技术栈**：Python、Streamlit、LangChain、ChromaDB、阿里云百炼（通义千问 `qwen-plus` + `text-embedding-v1`）
- **核心功能**：多格式文件上传与解析、智能文本分割、向量化存储与语义检索、基于文档内容的AI问答、引用来源展示、模块化架构设计
- **关键收获**：完整搭建了RAG全链路，理解了从文档解析到语义检索的每个环节，解决了ChromaDB模型下载超时、API配置错误、向量库集合冲突等多个实际问题

---

## 🛠️ 技术栈总览

| 类别 | 技术 |
|------|------|
| 编程语言 | Python |
| AI/大模型 | 通义千问API、Prompt Engineering、RAG全链路 |
| 框架与工具 | Streamlit、LangChain、ChromaDB |
| 版本控制与部署 | Git、GitHub、Streamlit Cloud |

---

## 👤 关于我

- **姓名**：袁朝阳
- **学校**：武汉工程科技学院 · 人工智能专业 · 本科在读（2023-2027）
- **求职意向**：AI应用开发实习生
- **GitHub**：[ych-yu](https://github.com/ych-yu)