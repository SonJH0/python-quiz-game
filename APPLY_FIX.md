# 피드백 수정 파일 적용 안내

이 ZIP은 원격 main 7a35753 기준으로 만들었습니다. GitHub는 아직 변경하지 않았습니다.
개인 state.json, backups/, .git 폴더는 포함하지 않았습니다. 기존 프로젝트에 파일을 덮어쓰면 개인 데이터와 Git 이력은 그대로 유지됩니다.
ZIP에 포함된 파이썬 파일만 따로 실행할 수도 있지만, 그 폴더에는 기존 Git 이력이 없으므로 원래 저장소에 적용해 제출합니다.

## 적용

1. 실행 중인 게임을 0으로 종료합니다.
2. ZIP을 다운로드합니다.
3. 원래 python-quiz-game 폴더의 VS Code 터미널에서 아래를 실행합니다. 파일 이름은 실제 다운로드 이름과 일치해야 합니다.

```powershell
Expand-Archive -Path "$env:USERPROFILE\Downloads\python-quiz-feedback-fix.zip" -DestinationPath . -Force
python -m unittest discover -s tests -v
python main.py
```

문제 수가 21개 이상이면 목록 화면에서 다음/이전 쪽을 선택할 수 있습니다.
백업은 새 코드로 저장할 때 생성됩니다. 예전 손실 데이터가 자동 복원되는 것은 아닙니다.

## GitHub 반영

테스트가 통과하고 프로그램이 실행되는 것을 확인한 뒤 실행합니다.

```powershell
git add README.md .gitignore storage.py quiz_game.py backup_state.py docs tests tools APPLY_FIX.md
git diff --cached --stat
git commit -m "Fix: 평가 피드백 증빙과 대량 목록 및 백업 복구 보완"
git push origin main
git status
```

처음 실행한 이후의 개인 백업은 Git에 올라가지 않습니다.
수정 파일 적용만으로 GitHub가 업데이트되지는 않으며 commit과 push가 필요합니다.

## 피드백 대응

| 항목 | 파일 |
|---|---|
| #5 실제 커밋 수와 스크린샷 | README.md, docs/commit-evidence.md, docs/evidence/commit-snapshot.json |
| #12 메시지 템플릿과 사례 | README.md, docs/commit-convention.md |
| #16 1000/10000개 측정과 메모리·검색 분석 | docs/scalability.md, tools/benchmark.py, quiz_game.py |
| #17 정상 백업 5개 및 손상 보존·자동/수동 복원 | storage.py, backup_state.py, docs/backup-recovery.md |

새 코드 자동 테스트는 Linux/Python 3.12.14에서 수행했습니다. Windows 실기 검증은 적용 후 위 명령으로 확인합니다.
