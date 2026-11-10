"""게임을 종료한 뒤 실행: python backup_state.py list / backup / restore latest"""
import argparse
from pathlib import Path
import storage


def main():
    parser = argparse.ArgumentParser(description="게임 데이터 백업 및 복원")
    parser.add_argument("command", choices=("list", "backup", "restore"))
    parser.add_argument("name", nargs="?")
    args = parser.parse_args()
    if args.command == "list":
        paths = storage.list_backups()
        for path in paths:
            print(path.name)
        if not paths:
            print("백업이 없습니다.")
        return 0
    if args.command == "backup":
        try:
            path = storage.create_backup(storage._read_state(storage.STATE_PATH))
            storage._prune_backups()
            print(f"수동 백업 완료: {path.name}")
            return 0
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"백업 실패: {error}")
            return 1
    if not args.name:
        parser.error("restore 다음에 latest 또는 백업 파일 이름을 입력해 주세요.")
    if args.name == "latest":
        for path in storage.list_backups():
            try:
                storage._read_state(path)
            except (OSError, ValueError, KeyError, TypeError):
                continue
            return 0 if storage.restore_backup(path) else 1
        print("복원할 정상 백업이 없습니다.")
        return 1
    if Path(args.name).name != args.name:
        parser.error("경로 대신 list에 표시된 파일 이름만 입력해 주세요.")
    return 0 if storage.restore_backup(storage.backup_directory() / args.name) else 1


if __name__ == "__main__":
    raise SystemExit(main())
