from quiz_game import QuizGame


def main():
    game = None

    try:
        game = QuizGame()
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 퀴즈 게임을 종료합니다.")
    finally:
        if game is not None:
            game.save_data()


if __name__ == "__main__":
    main()
