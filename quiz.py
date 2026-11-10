class Quiz:
    def __init__(self, question, choices, answer, hint=""):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def display(self):
        print(f"\n문제: {self.question}")

        for number, choice in enumerate(self.choices, start=1):
            print(f"{number}. {choice}")

    def is_correct(self, user_answer):
        return user_answer == self.answer

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }


if __name__ == "__main__":
    quiz = Quiz(
        question="파이썬에서 화면에 출력하는 함수는?",
        choices=["input()", "print()", "int()", "len()"],
        answer=2,
        hint="영어로 인쇄한다는 뜻입니다.",
    )

    quiz.display()
    print("2번을 선택하면:", quiz.is_correct(2))
    print("1번을 선택하면:", quiz.is_correct(1))
    print("저장용 데이터:", quiz.to_dict())