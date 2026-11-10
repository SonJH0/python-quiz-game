"""UTF-8 JSON 저장, 정상 스냅샷 5개 보관, 손상 파일 보존 및 자동 복구."""
import json
import math
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from default_quizzes import create_default_quizzes

STATE_PATH = Path(__file__).resolve().parent / "state.json"
BACKUP_KEEP = 5
_blocked_paths = set()
_archived_versions = set()


def create_default_state():
    return {"quizzes": [q.to_dict() for q in create_default_quizzes()],
            "best_score": None, "history": []}


def validate_state(data):
    if not isinstance(data, dict):
        raise ValueError("전체 데이터는 딕셔너리여야 합니다.")
    quizzes = data["quizzes"]
    if not isinstance(quizzes, list):
        raise ValueError("퀴즈 목록은 리스트여야 합니다.")
    for quiz in quizzes:
        if not isinstance(quiz, dict):
            raise ValueError("각 퀴즈는 딕셔너리여야 합니다.")
        if not isinstance(quiz["question"], str) or not quiz["question"].strip():
            raise ValueError("문제 내용이 올바르지 않습니다.")
        choices = quiz["choices"]
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")
        if any(not isinstance(c, str) or not c.strip() for c in choices):
            raise ValueError("선택지 내용이 올바르지 않습니다.")
        if type(quiz["answer"]) is not int or not 1 <= quiz["answer"] <= 4:
            raise ValueError("정답 번호는 1~4의 정수여야 합니다.")
        if not isinstance(quiz.get("hint", ""), str):
            raise ValueError("힌트는 문자열이어야 합니다.")
    _validate_score(data["best_score"], nullable=True)
    if not isinstance(data["history"], list):
        raise ValueError("게임 기록은 리스트여야 합니다.")
    for record in data["history"]:
        if not isinstance(record, dict):
            raise ValueError("게임 기록 항목은 딕셔너리여야 합니다.")
        if not isinstance(record["played_at"], str):
            raise ValueError("완료 시간은 문자열이어야 합니다.")
        datetime.fromisoformat(record["played_at"])
        total, correct, hints, points = [record[k] for k in
            ("question_count", "correct_count", "hint_count", "earned_points")]
        if any(type(x) is not int for x in (total, correct, hints, points)):
            raise ValueError("게임 기록의 개수와 획득 점수는 정수여야 합니다.")
        if total < 1 or not 0 <= correct <= total or not 0 <= hints <= total:
            raise ValueError("게임 기록의 개수 범위가 잘못되었습니다.")
        hinted_correct = (correct * 10 - points) / 5
        if (not 0 <= points <= correct * 10 or points % 5 or
                not max(0, hints - (total - correct)) <= hinted_correct <= min(hints, correct)):
            raise ValueError("힌트 사용 수와 획득 점수가 일치하지 않습니다.")
        _validate_score(record["score"])
        if record["score"] != round(points / (total * 10) * 100, 1):
            raise ValueError("게임 기록의 환산 점수가 일치하지 않습니다.")


def _validate_score(score, nullable=False):
    if score is None and nullable:
        return
    if type(score) not in (int, float) or not 0 <= score <= 100:
        raise ValueError("점수는 0~100의 숫자여야 합니다.")
    if not math.isfinite(score):
        raise ValueError("점수는 유한한 숫자여야 합니다.")


def _read_state(path):
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    validate_state(data)
    return data


def backup_directory():
    return STATE_PATH.parent / "backups"


def _unique_path(prefix):
    folder = backup_directory()
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return folder / f"{prefix}-{stamp}-{uuid4().hex[:8]}.json"


def _write_json(path, data, mode="w"):
    with path.open(mode, encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, allow_nan=False)
        file.flush()
        os.fsync(file.fileno())


def create_backup(data):
    """검증된 데이터만 독립 파일에 보관한다. 주 파일은 변경하지 않는다."""
    validate_state(data)
    path = _unique_path("state")
    try:
        _write_json(path, data, "x")
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def list_backups():
    return sorted(backup_directory().glob("state-*.json"), reverse=True)


def _prune_backups():
    for path in list_backups()[BACKUP_KEEP:]:
        try:
            path.unlink()
        except OSError as error:
            print(f"오래된 백업 정리 실패: {error}")


def _preserve_current(prefix="corrupt"):
    raw = STATE_PATH.read_bytes()
    identity = (str(STATE_PATH.resolve()), raw)
    if prefix == "corrupt" and identity in _archived_versions:
        return
    destination = _unique_path(prefix)
    shutil.copy2(STATE_PATH, destination)
    if prefix == "corrupt":
        _archived_versions.add(identity)
    print(f"원본 파일 보존: {destination.name}")


def _write_atomic(data):
    temporary_path = STATE_PATH.with_suffix(".json.tmp")
    try:
        _write_json(temporary_path, data)
        temporary_path.replace(STATE_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)


def _recover_or_default():
    for path in list_backups():
        try:
            data = _read_state(path)
            print(f"정상 백업에서 복구했습니다: {path.name}")
            print("복구 데이터는 다음 저장 시 state.json에 반영됩니다.")
            return data
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"사용할 수 없는 백업 건너뜀: {path.name}: {error}")
    print("사용 가능한 백업이 없어 기본 퀴즈로 시작합니다.")
    return create_default_state()


def load_state():
    key = str(STATE_PATH.resolve())
    _blocked_paths.discard(key)
    try:
        return _read_state(STATE_PATH)
    except FileNotFoundError:
        print("저장 파일이 없습니다. 백업을 확인합니다.")
    except (ValueError, KeyError, TypeError) as error:
        print(f"저장 데이터가 손상되었습니다: {error}")
        try:
            _preserve_current()
        except OSError as archive_error:
            _blocked_paths.add(key)
            print(f"손상 원본 보존 실패. 이번 실행의 저장을 차단합니다: {archive_error}")
    except OSError as error:
        _blocked_paths.add(key)
        print(f"저장 파일 읽기 실패. 원본 보호를 위해 이번 실행의 저장을 차단합니다: {error}")
    return _recover_or_default()


def save_state(data):
    try:
        validate_state(data)
        if str(STATE_PATH.resolve()) in _blocked_paths:
            print("원본 파일 보호로 저장이 차단되었습니다. 권한 확인 후 재실행해 주세요.")
            return False
        try:
            previous = _read_state(STATE_PATH)
            if previous == data:
                if not list_backups():
                    create_backup(previous)
                return True
        except FileNotFoundError:
            previous = data
        except (ValueError, KeyError, TypeError):
            _preserve_current()
            previous = data
        create_backup(previous)
        _write_atomic(data)
        _prune_backups()
        return True
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"데이터를 저장하지 못했습니다: {error}")
        return False


def restore_backup(path):
    """선택한 정상 백업 복원. 기존 파일은 before-restore 사본으로 보존."""
    try:
        path = Path(path).resolve()
        if path.parent != backup_directory().resolve() or not path.name.startswith("state-"):
            raise ValueError("프로젝트 backups 폴더의 state-*.json을 선택해 주세요.")
        data = _read_state(path)
        if STATE_PATH.exists():
            _preserve_current("before-restore")
        _write_atomic(data)
        _blocked_paths.discard(str(STATE_PATH.resolve()))
        print(f"백업 복원 완료: {path.name}")
        return True
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"백업 복원 실패: {error}")
        return False


if __name__ == "__main__":
    state = load_state()
    print(f"불러온 퀴즈: {len(state['quizzes'])}개")
    if save_state(state):
        print("state.json 저장 완료")
        print(f"저장 위치: {STATE_PATH}")
