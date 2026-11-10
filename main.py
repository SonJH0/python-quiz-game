def read_number(prompt, minimum, maximum):
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


def show_menu():
    print("\n=== 파이썬 기초 퀴즈 게임 ===")
    print("1. 퀴즈 풀기")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 최고 점수 확인")
    print("5. 퀴즈 삭제")
    print("6. 게임 기록 확인")
    print("0. 종료")


def main():
    features = {
        1: "퀴즈 풀기",
        2: "퀴즈 추가",
        3: "퀴즈 목록",
        4: "최고 점수 확인",
        5: "퀴즈 삭제",
        6: "게임 기록 확인",
    }

    while True:
        show_menu()
        choice = read_number("메뉴 번호: ", 0, 6)

        if choice == 0:
            print("퀴즈 게임을 종료합니다.")
            break

        print(f"{features[choice]} 기능은 앞으로 구현할 예정입니다.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 퀴즈 게임을 종료합니다.")