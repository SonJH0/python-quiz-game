# clone과 pull 실습 기록

## 실습 결과

2026-11-10에 아래 절차를 수행했습니다.

1. GitHub 저장소를 python-quiz-game-clone 폴더에 clone했습니다.
2. 복제한 폴더에서 docs/clone-practice.md를 생성했습니다.
3. 문서를 커밋하고 GitHub에 push했습니다.
4. 기존 python-quiz-game 폴더로 돌아왔습니다.
5. git pull origin main으로 변경사항을 가져왔습니다.
6. 문서 내용과 Git 상태를 확인했습니다.

## 실제 사용한 주요 명령어

상위 폴더에서 저장소를 복제했습니다.

```powershell
git clone https://github.com/SonJH0/python-quiz-game.git python-quiz-game-clone
cd python-quiz-game-clone
```

복제한 폴더에서 문서를 작성한 후 커밋하고 업로드했습니다.

```powershell
git add docs/clone-practice.md
git commit -m "Docs: 별도 폴더에서 clone 실습 기록 추가"
git push
```

기존 폴더에서 변경사항을 가져오고 확인했습니다.

```powershell
cd ..\python-quiz-game
git pull origin main
Get-Content -Encoding UTF8 .\docs\clone-practice.md
git status
```

## 변경 반영 확인

- 복제 폴더에서 생성한 커밋: ed35ee0
- 기존 폴더의 pull 결과: 65de08f에서 ed35ee0으로 Fast-forward
- 추가된 파일: docs/clone-practice.md
- Get-Content로 한글 문서 내용 확인
- git status에서 원격 main과 동기화 및 working tree clean 확인

clone과 pull은 터미널 실행 화면도 별도 제출 증빙으로 보관합니다.