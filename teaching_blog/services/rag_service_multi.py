"""
RAG知识库服务 - 支持多种LLM/Embedding提供商

支持的提供商：
1. Ollama (本地) - 免费，需要下载模型
2. OpenAI - 付费，API调用
3. Azure OpenAI - 企业版
4. HuggingFace - 免费，本地运行
5. 智谱AI (Zhipu) - 国内有免费额度
6. 自定义兼容接口

使用方式：
    通过环境变量或配置选择提供商
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeBase:
    """知识库数据类"""
    id: str
    name: str
    description: str
    created_at: str
    document_count: int = 0
    path: str = ""
    chroma_path: str = ""


class RAGKnowledgeService:
    """
    RAG知识库服务核心类 - 多模型支持版

    配置优先级（从高到低）：
    1. 环境变量
    2. config.json 配置文件
    3. 默认值（Ollama）
    """

    def __init__(self, provider: str = None):
        # 基础路径配置
        self.base_dir = os.path.join(os.getcwd(), 'rag_knowledge_base')
        self.kb_dir = os.path.join(self.base_dir, 'knowledge_bases')
        self.chroma_dir = os.path.join(self.base_dir, 'chroma_db')
        self.documents_dir = os.path.join(self.base_dir, 'documents')

        # 创建目录结构
        for directory in [self.base_dir, self.kb_dir, self.chroma_dir, self.documents_dir]:
            os.makedirs(directory, exist_ok=True)

        # 元数据存储文件
        self.metadata_file = os.path.join(self.base_dir, 'metadata.json')

        # 加载配置
        self.config = self._load_config()

        # 确定使用的提供商
        self.provider = provider or self.config.get('provider', 'ollama')
        logger.info(f"RAG服务将使用提供商: {self.provider}")

        # 初始化模型配置
        self._setup_provider_config()

        # 初始化嵌入模型和LLM
        self.embeddings = None
        self.llm = None

        # 加载元数据
        self._load_metadata()

        logger.info(f"RAG服务初始化完成，基础目录: {self.base_dir}")

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_file = os.path.join(self.base_dir, 'config.json')

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"配置文件读取失败: {e}")

        return {}

    def _save_config(self):
        """保存配置到文件"""
        config_file = os.path.join(self.base_dir, 'config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def _setup_provider_config(self):
        """根据提供商设置配置"""
        provider = self.provider.lower()

        if provider == 'ollama':
            self._setup_ollama()
        elif provider == 'openai':
            self._setup_openai()
        elif provider == 'azure':
            self._setup_azure_openai()
        elif provider == 'huggingface':
            self._setup_huggingface()
        elif provider == 'zhipu':
            self._setup_zhipu()
        else:
            logger.warning(f"未知提供商 '{provider}'，回退到 Ollama")
            self._setup_ollama()

    def _setup_ollama(self):
        """Ollama 配置（默认）"""
        self.ollama_base_url = os.environ.get(
            'OLLAMA_BASE_URL',
            self.config.get('ollama', {}).get('base_url', 'http://localhost:11434')
        )
        self.llm_model = os.environ.get(
            'LLM_MODEL',
            self.config.get('ollama', {}).get('llm_model', 'qwen3:8b')
        )
        self.embedding_model = os.environ.get(
            'EMBEDDING_MODEL',
            self.config.get('ollama', {}).get('embedding_model', 'qwen3-embedding:4b')
        )

        logger.info(f"[Ollama] LLM: {self.llm_model}, Embedding: {self.embedding_model}")

    def _setup_openai(self):
        """OpenAI API 配置"""
        self.openai_api_key = os.environ.get(
            'OPENAI_API_KEY',
            self.config.get('openai', {}).get('api_key', '')
        )
        self.openai_base_url = os.environ.get(
            'OPENAI_BASE_URL',
            self.config.get('openai', {}).get('base_url', None)
        )
        self.llm_model = os.environ.get(
            'LLM_MODEL',
            self.config.get('openai', {}).get('llm_model', 'gpt-4o-mini')
        )
        self.embedding_model = os.environ.get(
            'EMBEDDING_MODEL',
            self.config.get('openai', {}).get('embedding_model', 'text-embedding-3-small')
        )

        if not self.openai_api_key:
            raise ValueError("请设置 OPENAI_API_KEY 环境变量或在 config.json 中配置")

        logger.info(f"[OpenAI] LLM: {self.llm_model}, Embedding: {self.embedding_model}")

    def _setup_azure_openai(self):
        """Azure OpenAI 配置"""
        self.azure_api_key = os.environ.get(
            'AZURE_OPENAI_API_KEY',
            self.config.get('azure', {}).get('api_key', '')
        )
        self.azure_endpoint = os.environ.get(
            'AZURE_OPENAI_ENDPOINT',
            self.config.get('azure', {}).get('endpoint', '')
        )
        self.azure_deployment_name = os.environ.get(
            'AZURE_DEPLOYMENT_NAME',
            self.config.get('azure', {}).get('deployment_name', 'gpt-4')
        )
        self.azure_embedding_deployment = os.environ.get(
            'AZURE_EMBEDDING_DEPLOYMENT',
            self.config.get('azure', {}).get('embedding_deployment', 'text-embedding-ada-002'
        )
        )
        self.azure_api_version = os.environ.get(
            'AZURE_API_VERSION',
            self.config.get('azure', {}).get('api_version', '2024-02-01'
        )

        if not self.azure_api_key or not self.azure_endpoint:
            raise ValueError("请设置 AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT")

        logger.info(f"[Azure] Endpoint: {self.azure_endpoint}, Deployment: {self.azure_deployment_name}")

    def _setup_huggingface(self):
        """HuggingFace 本地模型配置"""
        self.hf_llm_model = os.environ.get(
            'HF_LLM_MODEL',
            self.config.get('huggingface', {}).get('llm_model', 'THUDM/chatglm3-6b')
        )
        self.hf_embedding_model = os.environ.get(
            'HF_EMBEDDING_MODEL',
            self.config.get('huggingface', {}).get('embedding_model', 'BAAI/bge-large-zh-v1.5')
        )
        self.device = os.environ.get(
            'HF_DEVICE',
            self.config.get('huggingface', {}).get('device', 'cpu')
        )

        logger.info(f"[HuggingFace] LLM: {self.hf_llm_model}, Embedding: {self.hf_embedding_model}")

    def _setup_zhipu(self):
        """智谱AI配置（国产）"""
        self.zhipu_api_key = os.environ.get(
            'ZHIPUAI_API_KEY',
            self.config.get('zhipu', {}).get('api_key', '')
        )
        self.llm_model = os.environ.get(
            'LLM_MODEL',
            self.config.get('zhipu', {}).get('llm_model', 'glm-4-flash')
        )
        self.embedding_model = os.environ.get(
            'EMBEDDING_MODEL',
            self.config.get('zhipu', {}).get('embedding_model', 'embedding-3')
        )

        if not self.zhipu_api_key:
            raise ValueError("请设置 ZHIPUAI_API_KEY 环境变量或在 config.json 中配置")

        logger.info(f"[Zhipu] LLM: {self.llm_model}, Embedding: {self.embedding_model}")

    def _load_metadata(self):
        """加载知识库元数据"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {'knowledge_bases': {}}
            self._save_metadata()

    def _save_metadata(self):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def reload_metadata(self):
        """强制从磁盘重新加载元数据"""
        self._load_metadata()
        logger.info("📂 元数据已从磁盘重新加载")

    # ==================== 模型初始化 ====================

    def _init_embeddings(self):
        """延迟初始化嵌入模型（根据provider自动选择）"""
        if self.embeddings is not None:
            return

        provider = self.provider.lower()
        logger.info(f"正在初始化 [{provider}] 嵌入模型...")

        if provider == 'ollama':
            from langchain_ollama import OllamaEmbeddings
            self.embeddings = OllamaEmbeddings(
                base_url=self.ollama_base_url,
                model=self.embedding_model
            )

        elif provider == 'openai':
            from langchain_openai import OpenAIEmbeddings
            kwargs = {
                'model': self.embedding_model,
                'openai_api_key': self.openai_api_key
            }
            if self.openai_base_url:
                kwargs['openai_api_base'] = self.openai_base_url
            self.embeddings = OpenAIEmbeddings(**kwargs)

        elif provider == 'azure':
            from langchain_openai import AzureOpenAIEmbeddings
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=self.azure_embedding_deployment,
                openai_api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint,
                api_key=self.azure_api_key
            )

        elif provider == 'huggingface':
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.hf_embedding_model,
                model_kwargs={'device': self.device}
            )

        elif provider == 'zhipu':
            from langchain_community.embeddings import ZhipuAIEmbeddings
            self.embeddings = ZhipuAIEmbeddings(
                zhipuai_api_key=self.zhipu_api_key,
                model=self.embedding_model
            )

        else:
            raise ValueError(f"不支持的提供商: {provider}")

        logger.info(f"✅ 嵌入模型初始化完成 ({provider})")

    def _init_llm(self):
        """延迟初始化LLM（根据provider自动选择）"""
        if self.llm is not None:
            return

        provider = self.provider.lower()
        logger.info(f"正在初始化 [{provider}] LLM...")

        if provider == 'ollama':
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(
                base_url=self.ollama_base_url,
                model=self.llm_model,
                temperature=0.7,
                num_ctx=4096
            )

        elif provider == 'openai':
            from langchain_openai import ChatOpenAI
            kwargs = {
                'model': self.llm_model,
                'temperature': 0.7,
                'openai_api_key': self.openai_api_key
            }
            if self.openai_base_url:
                kwargs['openai_api_base'] = self.openai_base_url
            self.llm = ChatOpenAI(**kwargs)

        elif provider == 'azure':
            from langchain_openai import AzureChatOpenAI
            self.llm = AzureChatOpenAI(
                azure_deployment=self.azure_deployment_name,
                openai_api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint,
                api_key=self.azure_api_key,
                temperature=0.7
            )

        elif provider == 'huggingface':
            from langchain_huggingface import HuggingFacePipeline
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

            logger.warning("[HuggingFace] 加载本地大型语言模型可能需要较长时间和大量内存...")

            tokenizer = AutoTokenizer.from_pretrained(self.hf_llm_model)
            model = AutoModelForCausalLM.from_pretrained(self.hf_llm_model)

            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                device=self.device
            )
            self.llm = HuggingFacePipeline(pipeline=pipe)

        elif provider == 'zhipu':
            from langchain_community.chat_models import ChatZhipuAI
            self.llm = ChatZhipuAI(
                zhipuai_api_key=self.zhipu_api_key,
                model=self.llm_model,
                temperature=0.7
            )

        else:
            raise ValueError(f"不支持的提供商: {provider}")

        logger.info(f"✅ LLM初始化完成 ({provider})")

    # ==================== 知识库管理 ====================

    def create_knowledge_base(self, name: str, description: str = "") -> Dict:
        """创建新的知识库"""
        self.reload_metadata()

        for kb_id, kb_info in self.metadata['knowledge_bases'].items():
            if kb_info['name'] == name:
                logger.warning(f"知识库名称已存在: {name} (ID: {kb_id})")
                return {
                    'success': False,
                    'error': f'知识库 "{name}" 已存在，请使用其他名称',
                    'existing_kb': KnowledgeBase(**kb_info).__dict__
                }

        kb_id = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + name.replace(' ', '_')

        kb_path = os.path.join(self.kb_dir, kb_id)
        os.makedirs(kb_path, exist_ok=True)

        chroma_path = os.path.join(self.chroma_dir, kb_id)

        kb_info = {
            'id': kb_id,
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'document_count': 0,
            'path': kb_path,
            'chroma_path': chroma_path
        }

        self.metadata['knowledge_bases'][kb_id] = kb_info
        self._save_metadata()

        logger.info(f"✅ 知识库创建成功: {name} (ID: {kb_id})")

        return {
            'success': True,
            'knowledge_base': KnowledgeBase(**kb_info).__dict__
        }

    def delete_knowledge_base(self, kb_id: str) -> Dict:
        """删除知识库及其所有数据"""
        if kb_id not in self.metadata['knowledge_bases']:
            return {'success': False, 'error': '知识库不存在'}

        kb_info = self.metadata['knowledge_bases'][kb_id]

        try:
            if os.path.exists(kb_info['path']):
                shutil.rmtree(kb_info['path'])

            if os.path.exists(kb_info.get('chroma_path', '')):
                shutil.rmtree(kb_info['chroma_path'])

            del self.metadata['knowledge_bases'][kb_id]
            self._save_metadata()

            logger.info(f"✅ 知识库删除成功: {kb_id}")
            return {'success': True}

        except Exception as e:
            logger.error(f"❌ 删除知识库失败: {e}")
            return {'success': False, 'error': str(e)}

    def list_knowledge_bases(self) -> List[Dict]:
        """获取所有知识库列表"""
        self.reload_metadata()

        kbs = []
        for kb_id, info in self.metadata['knowledge_bases'].items():
            kbs.append(KnowledgeBase(**info).__dict__)
        return kbs

    def get_knowledge_base(self, kb_id: str) -> Optional[Dict]:
        """获取单个知识库详情"""
        if kb_id in self.metadata['knowledge_bases']:
            return KnowledgeBase(**self.metadata['knowledge_bases'][kb_id]).__dict__
        return None

    # ==================== 文档上传与处理 ====================

    def upload_documents(
        self,
        kb_id: str,
        files: List[Tuple[str, bytes]],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        skip_vectorization: bool = False
    ) -> Dict:
        """上传文档（支持快速模式和完整模式）"""
        if kb_id not in self.metadata['knowledge_bases']:
            return {'success': False, 'error': '知识库不存在'}

        kb_info = self.metadata['knowledge_bases'][kb_id]
        doc_dir = os.path.join(self.documents_dir, kb_id)
        os.makedirs(doc_dir, exist_ok=True)

        uploaded_files = []
        all_documents = []

        try:
            for filename, content in files:
                filepath = os.path.join(doc_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(content)

                uploaded_files.append({
                    'filename': filename,
                    'path': filepath,
                    'size': len(content)
                })

                documents = self._load_document(filepath, filename)
                if documents:
                    all_documents.extend(documents)

            if not all_documents:
                return {
                    'success': False,
                    'error': '无法解析任何文档',
                    'uploaded_files': uploaded_files
                }

            self.metadata['knowledge_bases'][kb_id]['document_count'] += len(uploaded_files)
            self._save_metadata()

            if skip_vectorization:
                logger.info(f"✅ 文件已保存（跳过向量化）: {len(uploaded_files)} 个文件")
                return {
                    'success': True,
                    'uploaded_files': uploaded_files,
                    'total_chunks': 0,
                    'message': f'成功上传{len(uploaded_files)}个文件（已保存，待向量化）',
                    'vectorized': False
                }

            logger.info(f"开始向量化处理 {len(all_documents)} 个文档...")

            from langchain_text_splitters import RecursiveCharacterTextSplitter

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )

            chunks = text_splitter.split_documents(all_documents)
            logger.info(f"文档已切分为 {len(chunks)} 个文本块")

            logger.info("正在初始化嵌入模型...")
            self._init_embeddings()

            from langchain_chroma import Chroma

            chroma_path = kb_info.get('chroma_path',
                                      os.path.join(self.chroma_dir, kb_id))

            for i, chunk in enumerate(chunks):
                chunk.metadata['kb_id'] = kb_id
                chunk.metadata['chunk_index'] = i

            logger.info(f"正在生成 {len(chunks)} 个向量...")
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=chroma_path
            )
            vectorstore.persist()
            logger.info("✅ 向量化完成！")

            return {
                'success': True,
                'uploaded_files': uploaded_files,
                'total_chunks': len(chunks),
                'message': f'成功上传{len(uploaded_files)}个文件，生成{len(chunks)}个文本块',
                'vectorized': True
            }

        except Exception as e:
            logger.error(f"❌ 文档处理失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def _load_document(self, filepath: str, filename: str) -> List:
        """根据文件类型加载文档"""
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        try:
            if ext == 'pdf':
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(filepath)
            elif ext in ['txt', 'md']:
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(filepath, encoding='utf-8')
            elif ext in ['docx', 'doc']:
                try:
                    from langchain_community.document_loaders import UnstructuredWordLoader
                    loader = UnstructuredWordLoader(filepath)
                except ImportError:
                    logger.warning(f"Unstructured不可用，使用TextLoader处理 {filename}")
                    from langchain_community.document_loaders import TextLoader
                    loader = TextLoader(filepath, encoding='utf-8')
            else:
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(filepath, encoding='utf-8')

            documents = loader.load()

            for doc in documents:
                doc.metadata['source'] = filename

            return documents

        except Exception as e:
            logger.warning(f"加载文件 {filename} 失败: {e}")
            return []

    def get_documents(self, kb_id: str) -> List[Dict]:
        """获取知识库中的文档列表"""
        doc_dir = os.path.join(self.documents_dir, kb_id)

        if not os.path.exists(doc_dir):
            return []

        documents = []
        for filename in os.listdir(doc_dir):
            filepath = os.path.join(doc_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                documents.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size_formatted': self._format_size(stat.st_size)
                })

        return sorted(documents, key=lambda x: x['modified_time'], reverse=True)

    def delete_document(self, kb_id: str, filename: str) -> Dict:
        """删除指定文档"""
        doc_dir = os.path.join(self.documents_dir, kb_id)
        filepath = os.path.join(doc_dir, filename)

        if not os.path.exists(filepath):
            return {'success': False, 'error': '文件不存在'}

        try:
            os.remove(filepath)

            if kb_id in self.metadata['knowledge_bases']:
                current_count = self.metadata['knowledge_bases'][kb_id].get('document_count', 0)
                self.metadata['knowledge_bases'][kb_id]['document_count'] = max(0, current_count - 1)
                self._save_metadata()

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    # ==================== RAG问答 ====================

    def chat(
        self,
        kb_id: str,
        question: str,
        top_k: int = 5,
        return_sources: bool = True
    ) -> Dict:
        """RAG问答 - 带引用来源的智能回答"""
        if kb_id not in self.metadata['knowledge_bases']:
            return {'success': False, 'error': '知识库不存在'}

        try:
            self._init_embeddings()
            self._init_llm()

            from langchain_chroma import Chroma

            chroma_path = self.metadata['knowledge_bases'][kb_id].get(
                'chroma_path',
                os.path.join(self.chroma_dir, kb_id)
            )

            if not os.path.exists(chroma_path):
                return {
                    'success': False,
                    'error': '该知识库暂无文档数据，请先上传文档并完成向量化'
                }

            vectorstore = Chroma(
                persist_directory=chroma_path,
                embedding_function=self.embeddings
            )

            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            )

            docs = retriever.invoke(question)

            if not docs:
                return {
                    'success': True,
                    'answer': '抱歉，我在知识库中没有找到与您问题相关的内容。',
                    'sources': []
                }

            context_parts = []
            sources = []

            for i, doc in enumerate(docs[:top_k]):
                source_name = doc.metadata.get('source', f'文档{i+1}')
                similarity_score = getattr(doc, 'score', None)

                context_parts.append(f"[文档{i+1}] ({source_name})\n{doc.page_content}\n")

                sources.append({
                    'source': source_name,
                    'content': doc.page_content[:200] + ('...' if len(doc.page_content) > 200 else ''),
                    'score': round(similarity_score * 100, 1) if similarity_score else None,
                    'page': doc.metadata.get('page', None)
                })

            context = "\n".join(context_parts)

            prompt_template = """你是一个专业的教育知识助手。请根据以下提供的参考资料来回答用户的问题。

【参考资料】
{context}

【用户问题】
{question}

【回答要求】
1. 仅基于参考资料内容进行回答，不要编造信息
2. 如果资料中没有相关信息，请明确说明
3. 回答要准确、简洁、有条理
4. 引用具体的资料来源
5. 使用中文回答

【你的回答】"""

            from langchain.prompts import PromptTemplate
            from langchain.chains import RetrievalQA

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )

            result = qa_chain.invoke({"query": question})

            answer = result.get('result', '')

            avg_similarity = None
            valid_scores = [s['score'] for s in sources if s['score'] is not None]
            if valid_scores:
                avg_similarity = round(sum(valid_scores) / len(valid_scores), 1)

            response = {
                'success': True,
                'answer': answer,
                'question': question,
                'sources': sources if return_sources else [],
                'avg_similarity': avg_similarity,
                'model_used': f"{self.provider}:{self.llm_model}",
                'timestamp': datetime.now().isoformat(),
                'retrieved_docs': len(docs)
            }

            logger.info(f"✅ 问答完成，检索到 {len(docs)} 个相关文档")
            return response

        except Exception as e:
            logger.error(f"❌ 问答过程出错: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def chat_stream(self, kb_id: str, question: str, top_k: int = 5):
        """流式问答"""
        if kb_id not in self.metadata['knowledge_bases']:
            yield json.dumps({'error': '知识库不存在'}, ensure_ascii=False)
            return

        try:
            self._init_embeddings()
            self._init_llm()

            chroma_path = self.metadata['knowledge_bases'][kb_id].get(
                'chroma_path',
                os.path.join(self.chroma_dir, kb_id)
            )

            if not os.path.exists(chroma_path):
                yield json.dumps({'error': '该知识库暂无文档数据'})
                return

            from langchain_chroma import Chroma

            vectorstore = Chroma(
                persist_directory=chroma_path,
                embedding_function=self.embeddings
            )

            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": top_k}
            )

            docs = retriever.invoke(question)

            context_parts = []
            sources = []

            for i, doc in enumerate(docs):
                source_name = doc.metadata.get('source', f'文档{i+1}')
                context_parts.append(f"[文档{i+1}] ({source_name})\n{doc.page_content}\n")
                sources.append({
                    'source': source_name,
                    'content': doc.page_content[:200],
                    'score': round(getattr(doc, 'score', 0) * 100, 1) if hasattr(doc, 'score') else None
                })

            context = "\n".join(context_parts)

            prompt = f"""你是一个专业的教育知识助手。请根据以下参考资料回答问题。

【参考资料】
{context}

【问题】
{question}

【回答】"""

            for chunk in self.llm.stream(prompt):
                yield json.dumps({
                    'type': 'content',
                    'content': chunk.content,
                    'sources': sources
                }, ensure_ascii=False)

            yield json.dumps({'type': 'done'}, ensure_ascii=False)

        except Exception as e:
            yield json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)


# 全局单例实例
rag_service = None


def get_rag_service(provider: str = None) -> RAGKnowledgeService:
    """获取RAG服务实例（支持指定提供商）"""
    global rag_service
    if rag_service is None:
        rag_service = RAGKnowledgeService(provider=provider)
    return rag_service
