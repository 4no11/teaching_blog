"""
RAG知识库路由 - 提供完整的RESTful API

端点列表：
- 知识库管理：CRUD操作
- 文档管理：上传/删除/查询
- 问答对话：带引用来源的RAG问答
"""

import os
import json
from flask import request, jsonify, send_file, Response, session
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

from services.rag_service import RAGKnowledgeService, get_rag_service

logger = logging.getLogger(__name__)

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md', 'docx', 'doc', 'json', 'csv'}

# 全局服务实例
rag = None


def get_current_user_id():
    """获取当前登录用户的ID，未登录返回None"""
    return session.get('user_id')


def require_login():
    """检查用户是否已登录，未登录返回错误响应"""
    user_id = get_current_user_id()
    if not user_id:
        return False, jsonify({
            'success': False,
            'error': '请先登录后使用知识库功能',
            'redirect': '/login'
        }), 401
    return True, user_id


def get_service():
    """延迟初始化RAG服务（使用全局单例）"""
    global rag
    if rag is None:
        logger.info("首次初始化RAG服务...")
        rag = RAGKnowledgeService()
        logger.info("✅ RAG服务初始化完成")
    return rag


def register_rag_routes(app_or_bp):
    """注册所有RAG相关路由"""
    
    # ==================== 知识库管理 API ====================
    
    @app_or_bp.route('/api/rag/knowledge-bases', methods=['GET'])
    def list_knowledge_bases():
        """
        获取当前用户的知识库列表（需要登录）

        Response:
        {
            "success": true,
            "knowledge_bases": [...]
        }
        """
        try:
            # 检查登录状态
            logged_in, result = require_login()
            if not logged_in:
                return result

            user_id = result
            service = get_service()
            kbs = service.list_knowledge_bases(user_id=user_id)

            return jsonify({
                'success': True,
                'knowledge_bases': kbs,
                'total': len(kbs),
                'user_id': user_id
            })

        except Exception as e:
            logger.error(f"获取知识库列表失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app_or_bp.route('/api/rag/knowledge-bases', methods=['POST'])
    def create_knowledge_base():
        """
        创建新知识库（需要登录）

        Request JSON:
        {
            "name": "知识库名称",
            "description": "描述信息"
        }

        Response:
        {
            "success": true,
            "knowledge_base": {...}
        }
        """
        try:
            # 检查登录状态
            logged_in, result = require_login()
            if not logged_in:
                return result

            user_id = result
            data = request.get_json()
            name = data.get('name', '').strip()
            description = data.get('description', '')

            if not name:
                return jsonify({
                    'success': False,
                    'error': '请输入知识库名称'
                }), 400

            service = get_service()
            result = service.create_knowledge_base(name, description, user_id=user_id)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"创建知识库失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>', methods=['DELETE'])
    def delete_knowledge_base(kb_id):
        """删除知识库（需要登录且是所有者）"""
        try:
            # 检查登录状态
            logged_in, result = require_login()
            if not logged_in:
                return result

            user_id = result
            service = get_service()

            # 验证知识库是否属于当前用户
            kb = service.get_knowledge_base(kb_id)
            if not kb:
                return jsonify({'success': False, 'error': '知识库不存在'}), 404

            if kb.get('user_id') != user_id:
                return jsonify({
                    'success': False,
                    'error': '无权删除此知识库'
                }), 403

            result = service.delete_knowledge_base(kb_id)

            if not result.get('success'):
                return jsonify(result), 404

            return jsonify(result)

        except Exception as e:
            logger.error(f"删除知识库失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>', methods=['GET'])
    def get_knowledge_base_detail(kb_id):
        """获取知识库详情"""
        try:
            service = get_service()
            kb = service.get_knowledge_base(kb_id)
            
            if not kb:
                return jsonify({
                    'success': False,
                    'error': '知识库不存在'
                }), 404
            
            return jsonify({'success': True, 'knowledge_base': kb})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/status', methods=['GET'])
    def get_kb_status(kb_id):
        """获取知识库状态（文档数量、向量数等）"""
        try:
            service = get_service()
            kb = service.get_knowledge_base(kb_id)
            
            if not kb:
                return jsonify({'success': False, 'error': '不存在'}), 404
            
            documents = service.get_documents(kb_id)
            
            # 检查Chroma数据库是否存在
            chroma_path = os.path.join(
                service.chroma_dir, kb_id
            )
            has_vectors = os.path.exists(chroma_path) and \
                        len(os.listdir(chroma_path)) > 0
            
            return jsonify({
                'success': True,
                'status': {
                    'document_count': len(documents),
                    'has_vector_data': has_vectors,
                    'created_at': kb['created_at'],
                    'documents': documents[:5]  # 最近5个文件
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== 文档管理 API ====================
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/documents', methods=['POST'])
    def upload_documents(kb_id):
        """
        上传文档到知识库（需要登录且是所有者）

        Request: multipart/form-data
        - files: 文件数组

        Response:
        {
            "success": true,
            "uploaded_files": [...],
            "total_chunks": 150,
            "message": "..."
        }
        """
        try:
            # 检查登录状态
            logged_in, result = require_login()
            if not logged_in:
                return result

            user_id = result
            service = get_service()

            # 验证知识库是否属于当前用户
            kb = service.get_knowledge_base(kb_id)
            if not kb:
                return jsonify({'success': False, 'error': '知识库不存在'}), 404

            if kb.get('user_id') != user_id:
                return jsonify({
                    'success': False,
                    'error': '无权操作此知识库'
                }), 403

            if 'files' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '没有上传文件'
                }), 400

            files = request.files.getlist('files')

            # 获取原始文件名列表（前端传来的中文原名）
            import json as _json
            original_names_raw = request.form.get('original_names', '[]')
            try:
                original_names = _json.loads(original_names_raw)
            except:
                original_names = []

            if not files or all(f.filename == '' for f in files):
                return jsonify({
                    'success': False,
                    'error': '请选择要上传的文件'
                }), 400

            uploaded_files = []

            for idx, file in enumerate(files):
                if file and file.filename:
                    safe_filename = file.filename

                    # 从原始名称获取显示名和扩展名
                    display_name = original_names[idx] if idx < len(original_names) else safe_filename
                    ext = safe_filename.rsplit('.', 1)[-1].lower() if '.' in safe_filename else ''
                    if ext not in ALLOWED_EXTENSIONS:
                        continue

                    content = file.read()
                    uploaded_files.append((safe_filename, content, display_name))
            
            if not uploaded_files:
                return jsonify({
                    'success': False,
                    'error': '没有有效的文件（支持: PDF, TXT, MD, DOCX）'
                }), 400
            
            # 调用服务处理（默认使用快速模式，跳过向量化）
            service = get_service()
            result = service.upload_documents(
                kb_id=kb_id,
                files=uploaded_files,
                chunk_size=request.form.get('chunk_size', 500, type=int),
                chunk_overlap=request.form.get('chunk_overlap', 50, type=int),
                skip_vectorization=True  # 快速模式：只保存文件，不立即向量化
            )
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"文档上传失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/documents', methods=['GET'])
    def list_documents(kb_id):
        """
        获取知识库中的文档列表
        
        Query Params:
        - page: 页码
        - per_page: 每页数量
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            service = get_service()
            documents = service.get_documents(kb_id)
            
            # 分页
            start = (page - 1) * per_page
            end = start + per_page
            paginated_docs = documents[start:end]
            
            return jsonify({
                'success': True,
                'documents': paginated_docs,
                'total': len(documents),
                'page': page,
                'per_page': per_page,
                'pages': (len(documents) + per_page - 1) // per_page
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/documents/<filename>', methods=['DELETE'])
    def delete_document(kb_id, filename):
        """删除指定文档"""
        try:
            service = get_service()
            result = service.delete_document(kb_id, filename)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/documents/<filename>', methods=['GET'])
    def download_document(kb_id, filename):
        """下载文档"""
        try:
            service = get_service()
            doc_dir = os.path.join(service.documents_dir, kb_id)
            filepath = os.path.join(doc_dir, secure_filename(filename))
            
            if not os.path.exists(filepath):
                return jsonify({
                    'success': False,
                    'error': '文件不存在'
                }), 404
            
            return send_file(filepath, as_attachment=True, download_name=filename)

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/vectorize', methods=['POST'])
    def vectorize_documents(kb_id):
        """
        手动触发文档向量化（异步后台执行）

        Request JSON:
        {
            "chunk_size": 500,
            "chunk_overlap": 50
        }

        Response (立即返回):
        {
            "success": true,
            "message": "向量化任务已启动",
            "task_id": "kb_id"
        }
        """
        import threading

        try:
            service = get_service()

            # 检查知识库是否存在
            kb = service.get_knowledge_base(kb_id)
            if not kb:
                return jsonify({
                    'success': False,
                    'error': '知识库不存在'
                }), 404

            # 获取该知识库的所有文档
            documents = service.get_documents(kb_id)
            if not documents:
                return jsonify({
                    'success': False,
                    'error': '该知识库没有文档，请先上传文件'
                }), 400

            # 读取所有文档内容
            files = []
            doc_dir = os.path.join(service.documents_dir, kb_id)

            for doc in documents:
                filepath = os.path.join(doc_dir, doc['filename'])
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        content = f.read()
                    files.append((doc['filename'], content))

            if not files:
                return jsonify({
                    'success': False,
                    'error': '无法读取文档文件'
                }), 400

            # 获取参数
            data = request.get_json() or {}
            chunk_size = data.get('chunk_size', 500)
            chunk_overlap = data.get('chunk_overlap', 50)

            # 初始化进度追踪
            from services.vectorization_progress import get_progress_tracker
            progress_tracker = get_progress_tracker()

            # ✅ 检查是否已有任务在运行（防止重复启动）
            existing_progress = progress_tracker.get_progress(kb_id)
            if existing_progress and existing_progress['status'] == 'processing':
                return jsonify({
                    'success': False,
                    'error': '该知识库已有向量化任务正在运行中，请等待完成或刷新页面查看进度'
                }), 409  # 409 Conflict

            progress_tracker.start_task(kb_id, total_chunks=0)  # 先初始化，后面更新总数

            # 定义后台任务函数
            def run_vectorization():
                """在后台线程中执行向量化"""
                try:
                    logger.info(f"[后台] 开始向量化: {kb_id}")
                    result = service.upload_documents(
                        kb_id=kb_id,
                        files=files,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        skip_vectorization=False
                    )
                    logger.info(f"[后台] 向量化完成: {kb_id}, 结果: {result.get('success')}")
                except Exception as e:
                    logger.error(f"[后台] 向量化失败: {kb_id} - {e}")
                    import traceback
                    traceback.print_exc()
                    progress_tracker.fail_task(kb_id, str(e))

            # 启动后台线程（不等待完成）
            thread = threading.Thread(
                target=run_vectorization,
                name=f"vectorize-{kb_id[:8]}",
                daemon=True
            )
            thread.start()
            logger.info(f"✅ 向量化任务已在后台启动: {kb_id}")

            # 立即返回202 Accepted
            return jsonify({
                'success': True,
                'message': '向量化任务已启动，请通过进度API查询状态',
                'task_id': kb_id
            }), 202

        except Exception as e:
            logger.error(f"启动向量化失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app_or_bp.route('/api/rag/knowledge-bases/<kb_id>/progress', methods=['GET'])
    def get_vectorization_progress(kb_id):
        """
        查询向量化进度

        Response:
        {
            "status": "processing|completed|failed|null",
            "progress_percent": 50,
            "message": "正在生成向量 25/100...",
            "current_chunk": 25,
            "total_chunks": 100
        }
        """
        try:
            from services.vectorization_progress import get_progress_tracker

            tracker = get_progress_tracker()
            progress = tracker.get_progress(kb_id)

            if not progress:
                return jsonify({
                    'status': None,
                    'message': '没有进行中的向量化任务'
                })

            # 返回进度信息（不包含完整result以减少数据量）
            return jsonify({
                'status': progress['status'],
                'progress_percent': progress['progress_percent'],
                'message': progress['message'],
                'current_chunk': progress['current_chunk'],
                'total_chunks': progress['total_chunks'],
                'error': progress.get('error')
            })

        except Exception as e:
            logger.error(f"查询进度失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== RAG问答 API ====================
    
    @app_or_bp.route('/api/rag/chat', methods=['POST'])
    def chat():
        """
        RAG问答接口（非流式）
        
        Request JSON:
        {
            "kb_id": "knowledge_base_id",
            "question": "用户问题",
            "top_k": 5
        }
        
        Response:
        {
            "success": true,
            "answer": "...",
            "sources": [
                {
                    "source": "文件名.pdf",
                    "content": "引用内容片段",
                    "score": 89.5,
                    "page": 3
                },
                ...
            ],
            "avg_similarity": 87.2,
            "model_used": "qwen3:8b"
        }
        """
        try:
            data = request.get_json()
            kb_id = data.get('kb_id', '')
            question = data.get('question', '').strip()
            top_k = data.get('top_k', 5)
            
            if not question:
                return jsonify({
                    'success': False,
                    'error': '请输入问题'
                }), 400
            
            if not kb_id:
                return jsonify({
                    'success': False,
                    'error': '请选择知识库'
                }), 400
            
            service = get_service()
            result = service.chat(
                kb_id=kb_id,
                question=question,
                top_k=top_k,
                return_sources=True
            )
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"问答请求失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app_or_bp.route('/api/rag/chat/stream', methods=['POST'])
    def chat_stream():
        """
        流式问答接口（SSE）
        
        用于实时显示回答内容，体验更好
        """
        try:
            data = request.get_json()
            kb_id = data.get('kb_id', '')
            question = data.get('question', '').strip()
            top_k = data.get('top_k', 5)
            
            if not question or not kb_id:
                return jsonify({
                    'success': False,
                    'error': '缺少必要参数'
                }), 400
            
            service = get_service()
            
            def generate():
                for chunk in service.chat_stream(kb_id, question, top_k):
                    yield f"data: {chunk}\n\n"
                
                yield "data: [DONE]\n\n"
            
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== 历史记录 API（可选）====================
    
    @app_or_bp.route('/api/rag/chat/history', methods=['POST'])
    def save_chat_history():
        """保存聊天历史（需要登录）"""
        try:
            # 检查登录状态
            logged_in, result = require_login()
            if not logged_in:
                return result

            data = request.get_json()
            kb_id = data.get('kb_id')
            messages = data.get('messages', [])

            if not kb_id or not messages:
                return jsonify({'success': False, 'error': '参数不完整'})

            # 简单的本地存储方案（按用户隔离）
            user_id = result
            history_dir = os.path.join(
                get_service().base_dir, 'chat_history', str(user_id)
            )
            os.makedirs(history_dir, exist_ok=True)

            history_file = os.path.join(history_dir, f'{kb_id}.json')

            existing_history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    existing_history = json.load(f)

            # 添加新会话
            session = {
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'title': data.get('title', 'new'),
                'messages': messages,
                'created_at': datetime.now().isoformat(),
                'message_count': len(messages)
            }

            existing_history.insert(0, session)

            # 只保留最近50条会话
            existing_history = existing_history[:50]

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(existing_history, f, ensure_ascii=False, indent=2)

            return jsonify({
                'success': True,
                'session_id': session['id'],
                'message': '历史记录保存成功'
            })

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app_or_bp.route('/api/rag/chat/history/<kb_id>', methods=['GET'])
    def get_chat_history(kb_id):
        """获取聊天历史（需要登录）"""
        try:
            # 检查登录状态
            logged_in, result = require_login()
            if not logged_in:
                return result

            user_id = result
            history_file = os.path.join(
                get_service().base_dir, 'chat_history', str(user_id), f'{kb_id}.json'
            )
            
            if not os.path.exists(history_file):
                return jsonify({
                    'success': True,
                    'sessions': [],
                    'total': 0
                })
            
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            return jsonify({
                'success': True,
                'sessions': history,
                'total': len(history)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== 系统状态 API ====================
    
    @app_or_bp.route('/api/rag/status', methods=['GET'])
    def system_status():
        """获取RAG系统状态"""
        try:
            service = get_service()

            kbs = service.list_knowledge_bases()
            total_documents = sum(kb.get('document_count', 0) for kb in kbs)

            # 检查AI服务连接状态（根据实际provider）
            ai_service_status = 'unknown'
            try:
                import requests

                if service.provider == 'ollama':
                    # Ollama 本地服务
                    response = requests.get(
                        f'{service.ollama_base_url}/api/tags',
                        timeout=3
                    )
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m['name'] for m in models]
                        ai_service_status = {
                            'connected': True,
                            'models_available': model_names,
                            'has_llm': service.llm_model in model_names,
                            'has_embedding': service.embedding_model in model_names
                        }
                else:
                    # OpenAI 兼容接口 (SiliconFlow 等)
                    # ✅ 优化：只检查API端点可达性，不实际调用模型（避免触发RPM限制）
                    base_url_clean = service.openai_base_url.replace('/v1', '')

                    # 尝试 /models 端点（OpenAI 兼容）
                    test_response = requests.get(
                        f'{base_url_clean}/models',
                        headers={
                            'Authorization': f'Bearer {service.openai_api_key}'
                        },
                        timeout=5
                    )

                    if test_response.status_code == 200:
                        ai_service_status = {
                            'connected': True,
                            'models_available': [
                                service.llm_model,
                                service.embedding_model
                            ],
                            'provider': service.provider,
                            'base_url': base_url_clean.split('//')[1].split('/')[0],
                            'note': f'已配置 {service.llm_model} + {service.embedding_model}'
                        }
                    else:
                        # 如果 /models 不存在，尝试直接检查 base_url 可达性
                        try:
                            health_check = requests.get(
                                base_url_clean,
                                timeout=3
                            )
                            if health_check.status_code < 500:
                                ai_service_status = {
                                    'connected': True,
                                    'models_available': [
                                        service.llm_model,
                                        service.embedding_model
                                    ],
                                    'provider': service.provider,
                                    'base_url': base_url_clean.split('//')[1].split('/')[0],
                                    'note': f'已配置 {service.llm_model} + {service.embedding_model} (端点可达)'
                                }
                            else:
                                ai_service_status = {
                                    'connected': False,
                                    'error': f'服务不可用 ({health_check.status_code})'
                                }
                        except Exception as e:
                            ai_service_status = {
                                'connected': False,
                                'error': str(e)
                            }

            except Exception as e:
                ai_service_status = {'connected': False, 'error': str(e)}

            return jsonify({
                'success': True,
                'status': {
                    'knowledge_bases_count': len(kbs),
                    'total_documents': total_documents,
                    'ai_service': ai_service_status,
                    'provider': service.provider,
                    'base_directory': service.base_dir,
                    'chroma_db_path': service.chroma_dir
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    logger.info("✅ RAG知识库API路由注册完成")
    
    return app_or_bp
