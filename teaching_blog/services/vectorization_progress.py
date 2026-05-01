# -*- coding: utf-8 -*-
"""
向量化工序进度追踪器 - 实时反馈向量化状态

用法:
    from services.vectorization_progress import VectorizationProgress, get_progress_tracker

    tracker = get_progress_tracker()

    # 开始任务
    tracker.start_task(kb_id, total_chunks=100)

    # 更新进度
    tracker.update_progress(kb_id, current=50, status="正在生成向量...")

    # 完成
    tracker.complete_task(kb_id, result={...})

    # 查询进度
    progress = tracker.get_progress(kb_id)
"""

import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorizationProgress:
    """
    向量化进度追踪器（线程安全）

    功能:
    1. 跟踪多个知识库的向量化任务
    2. 提供实时进度百分比和状态信息
    3. 支持错误报告和完成状态
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def start_task(self, kb_id: str, total_chunks: int = 0):
        """开始新的向量化任务"""
        with self._lock:
            self._tasks[kb_id] = {
                'status': 'processing',
                'started_at': datetime.now().isoformat(),
                'completed_at': None,
                'total_chunks': total_chunks,
                'current_chunk': 0,
                'progress_percent': 0,
                'message': '初始化...',
                'result': None,
                'error': None
            }
            logger.info(f"[进度] 开始向量化任务: {kb_id}, 总块数: {total_chunks}")

    def update_progress(
        self,
        kb_id: str,
        current: int = None,
        total_chunks: int = None,
        message: str = None,
        status: str = None
    ):
        """更新任务进度"""
        with self._lock:
            if kb_id not in self._tasks:
                return

            task = self._tasks[kb_id]

            if total_chunks is not None:
                task['total_chunks'] = total_chunks

            if current is not None:
                task['current_chunk'] = current
                if task['total_chunks'] > 0:
                    task['progress_percent'] = min(100, int((current / task['total_chunks']) * 100))

            if message:
                task['message'] = message

            if status:
                task['status'] = status

            logger.debug(f"[进度] {kb_id}: {task['progress_percent']}% - {task['message']}")

    def complete_task(self, kb_id: str, result: Dict = None):
        """标记任务完成"""
        with self._lock:
            if kb_id in self._tasks:
                self._tasks[kb_id]['status'] = 'completed'
                self._tasks[kb_id]['completed_at'] = datetime.now().isoformat()
                self._tasks[kb_id]['progress_percent'] = 100
                self._tasks[kb_id]['message'] = '完成 - 向量化成功'
                self._tasks[kb_id]['result'] = result
                logger.info(f"[进度] 向量化完成: {kb_id}")

    def fail_task(self, kb_id: str, error: str):
        """标记任务失败"""
        with self._lock:
            if kb_id in self._tasks:
                self._tasks[kb_id]['status'] = 'failed'
                self._tasks[kb_id]['completed_at'] = datetime.now().isoformat()
                self._tasks[kb_id]['message'] = f'失败 - {error}'
                self._tasks[kb_id]['error'] = error
                logger.error(f"[进度] 向量化失败: {kb_id} - {error}")

    def get_progress(self, kb_id: str) -> Optional[Dict]:
        """获取任务进度"""
        with self._lock:
            if kb_id in self._tasks:
                return dict(self._tasks[kb_id])
            return None

    def get_all_progress(self) -> Dict[str, Dict]:
        """获取所有任务的进度"""
        with self._lock:
            return {k: dict(v) for k, v in self._tasks.items()}

    def clear_task(self, kb_id: str):
        """清除已完成的任务记录"""
        with self._lock:
            if kb_id in self._tasks and self._tasks[kb_id]['status'] in ['completed', 'failed']:
                del self._tasks[kb_id]


# 全局单例实例
_progress_tracker: Optional[VectorizationProgress] = None
_tracker_lock = threading.Lock()


def get_progress_tracker() -> VectorizationProgress:
    """获取全局进度追踪器实例"""
    global _progress_tracker
    with _tracker_lock:
        if _progress_tracker is None:
            _progress_tracker = VectorizationProgress()
        return _progress_tracker


def test_progress_tracker():
    """测试进度追踪器"""
    print("Testing VectorizationProgress...")

    tracker = VectorizationProgress()

    # 测试开始任务
    tracker.start_task("test_kb_1", total_chunks=100)
    progress = tracker.get_progress("test_kb_1")
    assert progress['status'] == 'processing'
    assert progress['total_chunks'] == 100
    print("[OK] Task started")

    # 测试更新进度
    tracker.update_progress("test_kb_1", current=25, message="Processing chunk 25...")
    progress = tracker.get_progress("test_kb_1")
    assert progress['progress_percent'] == 25
    assert progress['current_chunk'] == 25
    print("[OK] Progress updated to 25%")

    tracker.update_progress("test_kb_1", current=50, message="Halfway done!")
    progress = tracker.get_progress("test_kb_1")
    assert progress['progress_percent'] == 50
    print("[OK] Progress updated to 50%")

    # 测试完成任务
    tracker.complete_task("test_kb_1", result={'total_chunks': 100})
    progress = tracker.get_progress("test_kb_1")
    assert progress['status'] == 'completed'
    assert progress['progress_percent'] == 100
    print("[OK] Task completed")

    # 测试失败
    tracker.start_task("test_kb_2", total_chunks=50)
    tracker.fail_task("test_kb_2", error="Ollama connection failed")
    progress = tracker.get_progress("test_kb_2")
    assert progress['status'] == 'failed'
    assert progress['error'] == "Ollama connection failed"
    print("[OK] Task failure handled")

    # 测试多任务
    all_progress = tracker.get_all_progress()
    assert len(all_progress) == 2
    print(f"[OK] Multiple tasks tracked: {len(all_progress)}")

    print("\n[SUCCESS] All tests passed!")


if __name__ == '__main__':
    test_progress_tracker()
