import json
import math
from pathlib import Path

from default_quizzes import create_default_quizzes


STATE_PATH = Path(__file__).resolve().parent / "state.json"


def create_default_state():
    return {
        "quizzes": [
            quiz.to_dict()
            for quiz in create_default_quizzes()
        ],
        "best_score": None,
        "history": [],
    }


def validate_state(data):
    if not isinstance(data, dict):
        raise ValueError("전체 데이터는 딕셔너리여야 합니다.")

    quizzes = data["quizzes"]

    if not isinstance(quizzes, list):
        raise ValueError("퀴즈 목록은 리스트여야 합니다.")

    for quiz in quizzes:
        if not isinstance(quiz, dict):
            raise ValueError("각 퀴즈는 딕셔너리여야 합니다.")

        question = quiz["question"]
        choices = quiz["choices"]
        answer = quiz["answer"]
        hint = quiz.get("hint", "")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제 내용이 올바르지 않습니다.")

        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")

        for choice in choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("선택지 내용이 올바르지 않습니다.")

        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답 번호는 1~4의 정수여야 합니다.")

        if not isinstance(hint, str):
            raise ValueError("힌트는 문자열이어야 합니다.")

    best_score = data["best_score"]

    if best_score is not None:
        if type(best_score) not in (int, float):
            raise ValueError("최고 점수는 숫자여야 합니다.")

        if not 0 <= best_score <= 100 or not math.isfinite(best_score):
            raise ValueError("최고 점수는 0~100이어야 합니다.")

    if not isinstance(data["history"], list):
        raise ValueError("게임 기록은 리스트여야 합니다.")


def load_state():
    try:
        with STATE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        validate_state(data)
        return data

    except FileNotFoundError:
        print("저장 파일이 없어 기본 퀴즈로 시작합니다.")

    except (ValueError, KeyError, TypeError, UnicodeError) as error:
        print(f"저장 데이터가 손상되었습니다: {error}")
        print("기본 퀴즈 데이터로 시작합니다.")

    except OSError as error:
        print(f"저장 파일을 읽지 못했습니다: {error}")
        print("기본 퀴즈 데이터로 시작합니다.")

    return create_default_state()


def save_state(data):
    temporary_path = STATE_PATH.with_suffix(".json.tmp")

    try:
        validate_state(data)

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            )

        temporary_path.replace(STATE_PATH)
        return True

    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"데이터를 저장하지 못했습니다: {error}")
        return False


if __name__ == "__main__":
    state = load_state()
    print(f"불러온 퀴즈: {len(state['quizzes'])}개")

    if save_state(state):
        print("state.json 저장 완료")
        print(f"저장 위치: {STATE_PATH}")