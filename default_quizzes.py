from quiz import Quiz


def create_default_quizzes():
    return [
        Quiz(
            question="파이썬에서 화면에 내용을 출력하는 함수는?",
            choices=["input()", "print()", "int()", "len()"],
            answer=2,
            hint="영어로 인쇄한다는 뜻입니다.",
        ),
        Quiz(
            question="사용자가 키보드로 입력한 내용을 받는 함수는?",
            choices=["print()", "str()", "input()", "list()"],
            answer=3,
            hint="영어로 입력이라는 뜻입니다.",
        ),
        Quiz(
            question="정수 10의 자료형은?",
            choices=["int", "str", "bool", "list"],
            answer=1,
            hint="소수점이 없는 정수를 나타냅니다.",
        ),
        Quiz(
            question='문자열 "안녕하세요"의 자료형은?',
            choices=["int", "bool", "dict", "str"],
            answer=4,
            hint="문자들이 이어진 데이터를 나타냅니다.",
        ),
        Quiz(
            question="True와 False를 나타내는 자료형은?",
            choices=["list", "bool", "str", "dict"],
            answer=2,
            hint="참과 거짓을 표현합니다.",
        ),
        Quiz(
            question="여러 값을 순서대로 담는 리스트의 예시는?",
            choices=[
                '{"name": "민수"}',
                "True",
                "[10, 20, 30]",
                "100",
            ],
            answer=3,
            hint="대괄호 안에 여러 값을 나열합니다.",
        ),
        Quiz(
            question="키와 값을 짝지어 저장하는 자료형은?",
            choices=["dict", "int", "bool", "str"],
            answer=1,
            hint='{"name": "민수"}와 같은 형태입니다.',
        ),
        Quiz(
            question="조건에 따라 실행할 코드를 나눌 때 사용하는 것은?",
            choices=["def", "return", "import", "if"],
            answer=4,
            hint="영어로 만약이라는 뜻입니다.",
        ),
        Quiz(
            question="리스트의 각 항목을 하나씩 꺼내 반복할 때 알맞은 것은?",
            choices=["if", "for", "class", "try"],
            answer=2,
            hint="for item in items: 형태로 사용합니다.",
        ),
        Quiz(
            question="파이썬에서 함수를 정의할 때 사용하는 키워드는?",
            choices=["class", "except", "def", "break"],
            answer=3,
            hint="def 함수이름(): 형태로 작성합니다.",
        ),
    ]


if __name__ == "__main__":
    quizzes = create_default_quizzes()
    print(f"기본 퀴즈 수: {len(quizzes)}개")

    for number, quiz in enumerate(quizzes, start=1):
        print(f"\n--- {number}번 퀴즈 ---")
        quiz.display()
        print(f"정답 번호: {quiz.answer}")
        print(f"힌트: {quiz.hint}")