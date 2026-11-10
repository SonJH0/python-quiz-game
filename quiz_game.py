import random

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

    def offer_hint(self, quiz):
        if not quiz.hint.strip():
            print("이 문제에는 등록된 힌트가 없습니다.")
            return False

        print("힌트를 사용하면 정답 점수가 10점에서 5점으로 줄어듭니다.")
        choice = self.read_number(
            "힌트를 사용할까요? (1. 사용 / 2. 사용 안 함): ",
            1,
            2,
        )

        if choice == 1:
            print(f"힌트: {quiz.hint}")
            return True

        return False

    def play(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        available_count = len(self.quizzes)
        print(f"\n등록된 퀴즈는 총 {available_count}개입니다.")

        total = self.read_number(
            f"몇 문제를 풀까요? (1~{available_count}): ",
            1,
            available_count,
        )

        selected_quizzes = random.sample(self.quizzes, total)
        correct_count = 0
        hint_count = 0
        earned_points = 0

        for number, quiz in enumerate(selected_quizzes, start=1):
            print(f"\n--- {number}/{total}번 문제 ---")
            quiz.display()

            used_hint = self.offer_hint(quiz)

            if used_hint:
                hint_count += 1

            answer = self.read_number("정답 번호: ", 1, 4)

            if quiz.is_correct(answer):
                correct_count += 1
                points = 5 if used_hint else 10
                earned_points += points
                print(f"정답입니다! {points}점을 얻었습니다.")
            else:
                correct_choice = quiz.choices[quiz.answer - 1]
                print(f"오답입니다. 정답: {quiz.answer}. {correct_choice}")
                print("이번 문제의 획득 점수는 0점입니다.")

        score = round(earned_points / (total * 10) * 100, 1)

        print("\n=== 게임 결과 ===")
        print(f"전체 문제: {total}개")
        print(f"맞힌 문제: {correct_count}개")
        print(f"힌트 사용: {hint_count}회")
        print(f"획득 점수: {earned_points}/{total * 10}점")
        print(f"100점 환산 점수: {score:.1f}점")

        self.update_best_score(score)

        if not self.save_data():
            print("이번 결과를 파일에 저장하지 못했습니다.")
            print("종료할 때 저장을 다시 시도합니다.")

    def update_best_score(self, score):
        if self.best_score is None:
            self.best_score = score
            print("첫 최고 점수를 기록했습니다.")
        elif score > self.best_score:
            self.best_score = score
            print("최고 점수를 갱신했습니다.")
        else:
            print(f"기존 최고 점수: {self.best_score:.1f}점")

    def show_best_score(self):
        print("\n=== 최고 점수 ===")

        if self.best_score is None:
            print("아직 완료한 게임이 없습니다.")
            return

        print(f"최고 점수: {self.best_score:.1f}점 / 100점")

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

    def list_quizzes(self):
        print("\n=== 퀴즈 목록 ===")

        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        print(f"전체 퀴즈: {len(self.quizzes)}개")

        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"{number}. {quiz.question}")

    def delete_quiz(self):
        print("\n=== 퀴즈 삭제 ===")

        if not self.quizzes:
            print("삭제할 퀴즈가 없습니다.")
            return

        self.list_quizzes()

        number = self.read_number(
            f"삭제할 문제 번호 (1~{len(self.quizzes)}, 0: 취소): ",
            0,
            len(self.quizzes),
        )

        if number == 0:
            print("삭제를 취소했습니다.")
            return

        quiz = self.quizzes[number - 1]
        print(f"\n삭제할 문제: {quiz.question}")

        confirmation = self.read_number(
            "정말 삭제할까요? (1. 삭제 / 2. 취소): ",
            1,
            2,
        )

        if confirmation == 2:
            print("삭제를 취소했습니다.")
            return

        self.quizzes.pop(number - 1)

        if self.save_data():
            print(f"퀴즈를 삭제했습니다. 현재 총 {len(self.quizzes)}개입니다.")
        else:
            print("메모리에서는 삭제됐지만 파일 저장에 실패했습니다.")
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
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_best_score()
            elif choice == 5:
                self.delete_quiz()
            else:
                print("아직 구현하지 않은 기능입니다.")