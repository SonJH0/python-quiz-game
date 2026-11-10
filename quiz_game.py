from quiz import Quiz
from storage import load_state, save_state


class QuizGame:
    def __init__(self):
        self.quizzes = []
        self.best_score = None
        self.history = []
        self.load_data()

    def load_data(self):
        state = load_state()

        self.quizzes = [
            Quiz(
                question=item["question"],
                choices=item["choices"],
                answer=item["answer"],
                hint=item.get("hint", ""),
            )
            for item in state["quizzes"]
        ]

        self.best_score = state["best_score"]
        self.history = state["history"]

    def save_data(self):
        state = {
            "quizzes": [
                quiz.to_dict()
                for quiz in self.quizzes
            ],
            "best_score": self.best_score,
            "history": self.history,
        }

        success = save_state(state)

        if success:
            print("게임 데이터를 저장했습니다.")

        return success

    def read_number(self, prompt, minimum, maximum):
        while True:
            text = input(prompt).strip()

            if not text:
                print("빈 입력입니다. 숫자를 입력해 주세요.")
                continue

            try:
                number = int(text)
            except ValueError:
                print("숫자로 입력해 주세요.")
                continue

            if minimum <= number <= maximum:
                return number

            print(f"{minimum}부터 {maximum}까지 입력해 주세요.")

    def read_text(self, prompt):
        while True:
            text = input(prompt).strip()

            if text:
                return text

            print("내용을 입력해 주세요. 공백만 입력할 수 없습니다.")

    def show_menu(self):
        print("\n=== 파이썬 기초 퀴즈 게임 ===")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 최고 점수 확인")
        print("5. 퀴즈 삭제")
        print("6. 게임 기록 확인")
        print("0. 종료")

    def play(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        correct_count = 0
        total = len(self.quizzes)

        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"\n--- {number}/{total}번 문제 ---")
            quiz.display()

            answer = self.read_number("정답 번호: ", 1, 4)

            if quiz.is_correct(answer):
                print("정답입니다!")
                correct_count += 1
            else:
                correct_choice = quiz.choices[quiz.answer - 1]
                print(f"오답입니다. 정답: {quiz.answer}. {correct_choice}")

        earned_points = correct_count * 10
        score = round(earned_points / (total * 10) * 100, 1)

        print("\n=== 게임 결과 ===")
        print(f"전체 문제: {total}개")
        print(f"맞힌 문제: {correct_count}개")
        print(f"획득 점수: {earned_points}/{total * 10}점")
        print(f"100점 환산 점수: {score:.1f}점")

    def add_quiz(self):
        print("\n=== 퀴즈 추가 ===")

        question = self.read_text("문제 내용: ")

        choices = []

        for number in range(1, 5):
            choice = self.read_text(f"선택지 {number}: ")
            choices.append(choice)

        answer = self.read_number("정답 번호 (1~4): ", 1, 4)
        hint = input("힌트 (생략하려면 Enter): ").strip()

        quiz = Quiz(
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
        )

        self.quizzes.append(quiz)

        if self.save_data():
            print(f"퀴즈를 추가했습니다. 현재 총 {len(self.quizzes)}개입니다.")
        else:
            print("퀴즈는 메모리에 추가됐지만 파일 저장에 실패했습니다.")
            print("종료할 때 저장을 다시 시도합니다.")

    def run(self):
        while True:
            self.show_menu()
            choice = self.read_number("메뉴 번호: ", 0, 6)

            if choice == 0:
                print("퀴즈 게임을 종료합니다.")
                break
            elif choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            else:
                print("아직 구현하지 않은 기능입니다.")