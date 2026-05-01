# RAG知识库问答系统 - 使用指南

## 🚀 快速启动（3步）

### 第1步：安装依赖

```bash
cd teaching_blog
pip install langchain langchain-community langchain-core chromadb
pip install ollama unstructured python-multipart pypdf python-docx
```

### 第2步：启动Ollama服务并下载模型

```bash
# 1. 安装Ollama（如果还没安装）
# Windows: 从 https://ollama.ai 下载安装包

# 2. 启动Ollama服务（安装后会自动运行）
# 或在终端运行: ollama serve

# 3. 下载所需模型（首次使用）
ollama pull qwen3:8b           # LLM大模型 (4.7GB)
ollama pull qwen3-embedding:4b # 嵌入模型 (1.6GB)

# 验证模型是否就绪
ollama list
```

### 第3步：启动Web应用

```bash
python app.py
# 访问: http://localhost:5000/rag-knowledge
```

---

## ✨ 功能特性

### 1️⃣ **知识库管理**
- ✅ 创建/删除知识库
- ✅ 知识库列表展示
- ✅ 文档数量统计

### 2️⃣ **文档管理**
- ✅ 支持多文件上传（拖拽或点击）
- ✅ 支持格式：PDF、TXT、MD、DOCX
- ✅ 自动文本切片和向量化
- ✅ 文档列表查看和删除

### 3️⃣ **智能问答**
- ✅ RAG检索增强生成
- ✅ 显示引用来源（文件名 + 相似度分数）
- ✅ 支持多轮对话
- ✅ 历史记录保存

### 4️⃣ **系统监控**
- ✅ Ollama连接状态检测
- ✅ 模型可用性检查
- ✅ 知识库统计信息

---

## 📋 API接口文档

所有API基础路径: `/api/rag`

### 知识库管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/knowledge-bases` | 获取所有知识库 |
| POST | `/knowledge-bases` | 创建新知识库 |
| DELETE | `/knowledge-bases/<id>` | 删除知识库 |
| GET | `/knowledge-bases/<id>/status` | 获取知识库状态 |

**创建知识库示例:**
```bash
curl -X POST http://localhost:5000/api/rag/knowledge-bases \
  -H "Content-Type: application/json" \
  -d '{"name": "Python教程", "description": "Python编程相关资料"}'
```

### 文档管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/knowledge-bases/<id>/documents` | 上传文档 |
| GET | `/knowledge-bases/<id>/documents` | 获取文档列表 |
| DELETE | `/knowledge-bases/<id>/<filename>` | 删除文档 |

**上传文档示例:**
```bash
curl -X POST http://localhost:5000/api/rag/knowledge-base_id/documents \
  -F "files=@document1.pdf" \
  -F "files=@notes.txt"
```

### 问答接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/chat` | RAG问答（非流式）|
| POST | `/chat/stream` | 流式问答（SSE）|

**问答示例:**
```bash
curl -X POST http://localhost:5000/api/rag/chat \
  -H "Content-Type: application/json" \
  -d '{
    "kb_id": "your_kb_id",
    "question": "Python中的装饰器是什么？",
    "top_k": 5
  }'
```

**响应格式:**
```json
{
  "success": true,
  "answer": "装饰器是Python的一个高级功能...",
  "sources": [
    {
      "source": "python_advanced.pdf",
      "content": "装饰器是一种特殊的函数...",
      "score": 89.5,
      "page": 15
    }
  ],
  "avg_similarity": 87.2,
  "model_used": "qwen3:8b"
}
```

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│            前端界面 (Flask Templates)     │
│   ┌──────────┐ ┌──────────┐ ┌────────┐ │
│   │ 知识库   │ │ 文档上传 │ │ 问答   │ │
│   │ 管理     │ │ 处理     │ │ 对话   │ │
│   └────┬─────┘ └────┬─────┘ └───┬────┘ │
├────────┼────────────┼────────────┼─────┤
│        │            │            │     │
│   POST /upload   POST /chat   GET /list│
│        │            │            │     │
├────────▼────────────▼────────────▼─────┤
│         后端服务 (Flask + LangChain)      │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │       文档处理流程               │    │
│  │  加载 → 切片 → 向量化 → 存储     │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────▼──────────────────┐    │
│  │       问答检索流程               │    │
│  │  查询 → 向量搜索 → 上下文拼接    │    │
│  │       → LLM生成 → 返回答案      │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│              底层组件                    │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ ChromaDB │ │ Ollama   │ │LangChain│ │
│  │ 向量数据库│ │ LLM+嵌入 │ │ 框架   │ │
│  └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────┘
```

---

## ⚙️ 配置选项

### 环境变量

```bash
# Ollama服务地址（默认本地）
export OLLAMA_BASE_URL=http://localhost:11434

# 可选：修改默认模型
# 在 services/rag_service.py 中修改:
# self.llm_model = 'qwen3:8b'
# self.embedding_model = 'qwen3-embedding:4b'
```

### 文本切片参数

在上传文档时可调整：
- **chunk_size**: 切片大小（默认500字符）
  - 较小值：更精确的检索，但可能丢失上下文
  - 较大值：保留更多上下文，但可能引入噪声
  
- **chunk_overlap**: 重叠大小（默认50字符）
  - 保证切片间的连续性

---

## 🔧 故障排除

### 问题1: Ollama连接失败

**症状**: 左下角显示"Ollama未连接"

**解决方案**:
```bash
# 检查Ollama是否运行
ollama list

# 如果未运行，启动它
ollama serve

# Windows用户确保Ollama桌面应用已启动
```

### 问题2: 模型未找到

**症状**: 问答时返回错误

**解决方案**:
```bash
# 下载必需的模型
ollama pull qwen3:8b
ollama pull qwen3-embedding:4b

# 验证
ollama list
# 应该看到 qwen3:8b 和 qwen3-embedding:4b
```

### 问题3: 上传文档后无法回答问题

**可能原因**: 
- Chroma数据库未正确初始化
- 文档解析失败

**排查步骤**:
1. 检查 `teaching_blog/rag_knowledge_base/chroma_db/` 目录是否存在
2. 查看日志是否有错误信息
3. 尝试重新上传文档

### 问题4: 回答质量不佳

**优化建议**:
1. **增加相关文档**: 上传更多高质量参考资料
2. **调整切片参数**: 尝试不同的 chunk_size
3. **优化提问方式**: 使用更具体的问题
4. **增加 top_k**: 在前端选择更大的 k 值（如 8-10）

---

## 📊 性能参考

基于测试环境（RTX 3060 12GB）:

| 操作 | 耗时 | 说明 |
|------|------|------|
| 创建知识库 | <1秒 | 仅元数据操作 |
| 上传PDF（10页）| 5-10秒 | 包含解析+切片+向量化 |
| 单次问答 | 2-5秒 | 取决于top_k和内容长度 |
| 向量检索 | <1秒 | Chroma高效检索 |

---

## 💡 使用技巧

### 1. **构建高质量知识库**

✅ **推荐做法:**
- 使用结构化文档（教材、论文、技术文档）
- 保持文档语言一致（中文为主）
- 避免过短或过长的文档
- 定期更新和维护

❌ **避免:**
- 上传大量无关文档
- 使用扫描版PDF（OCR效果差）
- 混合多种语言的文档

### 2. **优化问答效果**

**好的提问示例:**
- "Python中装饰器的作用是什么？"
- "如何实现二叉树的遍历？请给出代码示例"
- "机器学习中过拟合的解决方法有哪些？"

**不好的提问:**
- "帮我写个程序"（太模糊）
- "这个怎么做？"（缺少上下文）

### 3. **引用来源解读**

每个回答都会显示引用来源：
- **文件名**: 来源文档
- **相似度分数**: 与问题的匹配程度
  - >90%: 高度相关，可信度高
  - 70-90%: 相关，可参考
  - <70%: 可能相关性较低

---

## 🔒 安全注意事项

1. **数据隐私**: 所有数据存储在本地，不会上传云端
2. **访问控制**: 当前版本无权限管理（按需求去掉）
3. **文件安全**: 仅允许特定格式上传，防止恶意文件
4. **Ollama安全**: 默认仅监听本地，不暴露到网络

---

## 📈 扩展建议

### 未来可添加的功能：

1. **多模态支持** - 图片/表格理解
2. **对话历史持久化** - 数据库存储而非文件
3. **批量导入** - 从URL/网盘导入文档
4. **知识图谱可视化** - 展示文档关系
5. **多知识库联合查询** - 跨库检索
6. **导出功能** - 导出对话为Markdown/PDF

---

## 📞 技术支持

如遇问题：
1. 检查本文档的故障排除部分
2. 查看终端错误日志
3. 确认Ollama服务正常运行
4. 验证依赖包完整安装

---

**祝您使用愉快！🎉**
