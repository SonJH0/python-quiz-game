"""실제 게임 데이터를 변경하지 않는 JSON 전체 저장/로드/메모리 측정."""
import contextlib
import copy
import io
import json
from pathlib import Path
import platform
import statistics
import sys
import tempfile
import time
import tracemalloc
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import storage
from quiz_game import QuizGame


def measure(count, repeats=5):
    base = storage.create_default_state()['quizzes']
    data = {'quizzes': [], 'best_score': None, 'history': []}
    for index in range(count):
        quiz = copy.deepcopy(base[index % len(base)])
        quiz['question'] = f"문제 {index + 1}: {quiz['question']}"
        data['quizzes'].append(quiz)
    with tempfile.TemporaryDirectory() as folder, patch.object(storage, 'STATE_PATH', Path(folder) / 'state.json'):
        saves, loads, startups = [], [], []
        with contextlib.redirect_stdout(io.StringIO()):
            for run in range(repeats):
                data['best_score'] = run
                start = time.perf_counter()
                if not storage.save_state(data):
                    raise RuntimeError('저장 실패')
                saves.append((time.perf_counter() - start) * 1000)
                start = time.perf_counter()
                loaded = storage.load_state()
                loads.append((time.perf_counter() - start) * 1000)
                assert len(loaded['quizzes']) == count
                start = time.perf_counter()
                game = QuizGame()
                startups.append((time.perf_counter() - start) * 1000)
                assert len(game.quizzes) == count
                del loaded, game
            tracemalloc.start()
            game = QuizGame()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        return {'quiz_count': count, 'json_bytes': storage.STATE_PATH.stat().st_size,
                'save_with_backup_median_ms': round(statistics.median(saves), 3),
                'load_validate_median_ms': round(statistics.median(loads), 3),
                'load_and_objects_median_ms': round(statistics.median(startups), 3),
                'load_python_peak_mib': round(peak / 1024**2, 3),
                'repeats': repeats}


if __name__ == '__main__':
    print(json.dumps({'python': platform.python_version(), 'platform': platform.platform(),
                      'results': [measure(1000), measure(10000)],
                      'scope': '임시 폴더, 생성 데이터, 게임 기록 0개, Python 할당 최고치; 전체 RSS 아님'},
                     ensure_ascii=False, indent=2))
