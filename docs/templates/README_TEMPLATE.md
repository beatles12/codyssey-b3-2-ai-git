# (Step 8) 제출용 README 작성 틀

> 사용법: 이 파일 내용을 저장소 루트의 `README.md` 에 복사한 뒤, `✏️` 표시가 있는 곳을 **내 결과로** 채우세요.
> 다 채우면 `✏️` 와 이 안내 상자를 지우고 `python -m learning_kit.practice 8` 로 확인합니다.
> 공식 필수 항목: 설치·실행 방법 / 환경변수(API Key) 설정 / 커밋·PR 명령 예시 / 출력 예시 / (민감정보 대응 또는 비용·요청 횟수 안내) 1개 이상

---

# AI 커밋 메시지 · PR 초안 생성기 (B3-2)

`git status` 와 `git diff` 로 내 변경 사항을 모아 AI API 에 보내고,
**커밋 메시지**와 **PR 제목·본문 초안**을 터미널에 출력하는 Python CLI 도구입니다.

> AI 가 만든 문구는 **초안**입니다. 반드시 내용을 검토한 뒤 직접 커밋·PR 에 적용하세요.

## 1. 설치

- 필요: Python 3.10 이상, Git
- 외부 패키지 없음 (표준 라이브러리만 사용)

```bash
git clone ✏️(내 저장소 주소)
cd ✏️(폴더 이름)
python --version
```

## 2. 환경변수(API Key) 설정

API Key 는 코드나 파일에 쓰지 않고 **환경변수**로만 설정합니다.

```bash
# Mac / Linux
export AI_API_KEY="YOUR_KEY"
# Windows PowerShell
$env:AI_API_KEY="YOUR_KEY"
```

✏️ 사용한 AI 제공자와 모델: (예: anthropic / claude-haiku-4-5) — 기본값은 `ai_gitgen/config.py`

## 3. 사용법

Git 이 초기화된 **프로젝트 루트**에서 실행합니다.

```bash
python main.py commit                     # 커밋 메시지 초안
python main.py pr                         # PR 제목/본문 초안
python main.py commit --safe-mode         # 민감정보 마스킹 + 전송 제한
python main.py pr --temperature 0.2 --max-tokens 400 --model ✏️모델이름
```

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--model` | 사용할 모델 이름 | ✏️ |
| `--temperature` | 0.0~1.0. 낮을수록 일관됨, 높을수록 다양함 | ✏️ |
| `--max-tokens` | 출력 길이 상한 (비용 상한) | ✏️ |
| `--safe-mode` | 민감정보 마스킹 ✏️(전송 제한을 구현했다면: + 최대 10파일·200줄만 전송) | 꺼짐 |
| ✏️ (선택) `--dry-run` | AI 를 부르지 않고 보낼 프롬프트만 확인 | 꺼짐 |

## 4. 출력 예시

### 커밋 메시지

```text
✏️ (실제로 python main.py commit 을 실행한 결과를 붙여 넣기. 키·개인정보가 없는지 확인!)
[INFO] Git status 수집 완료: ...
...
--- Commit Message ---
feat: ...
----------------------------------------
```

### PR 초안

```text
✏️ (실제 python main.py pr 결과)
--- PR Title ---
...
--- PR Body ---
## Why
- ...
## What
- ...
## How to Test
- ...
----------------------------------------
```

### 오류 상황

```text
✏️ API Key 가 없을 때 / 변경 사항이 없을 때 출력
```

## 5. 파라미터 실험 결과

| 조건 | 결과 요약 (길이·디테일) |
|---|---|
| ✏️ `--max-tokens 60` | |
| ✏️ `--max-tokens 600` | |
| ✏️ (가능하면) `--temperature 0.0` vs `1.0` | |

✏️ 내가 기본값을 이렇게 정한 이유:

## 6. 주의사항 (보안 · 비용)

- **민감정보**: git diff 에 API Key·비밀번호·이메일 같은 개인정보가 들어 있을 수 있습니다.
  `--safe-mode` 를 켜면 ✏️(내가 가리는 패턴) 을 `[MASKED]` 로 바꿉니다. ✏️(전송 제한을 구현했다면) 최대 10개 파일·200줄만 보냅니다.
- **비용 / 요청 횟수**: 한 번 실행할 때 AI API 를 ✏️1회만 호출하며 로그에 호출 횟수를 표시합니다.
  diff 가 크면 비용이 늘어나므로 `--safe-mode` 나 작은 단위 커밋을 권장합니다.
- **검토 필수**: 생성된 문구는 최종 정답이 아닙니다. 사실과 다른 내용이 없는지 확인한 뒤 사용하세요.
- 이 도구는 `git push` 나 GitHub PR 생성을 하지 않습니다. 초안 텍스트 출력까지만 합니다.

## 7. 프로젝트 구조

```text
main.py                    실행 파일
ai_gitgen/cli.py           명령줄 옵션, 전체 흐름
ai_gitgen/git_collector.py git status / diff 수집
ai_gitgen/safety.py        safe-mode (마스킹, 전송 제한)
ai_gitgen/prompt_builder.py 프롬프트 구성
ai_gitgen/ai_client.py     AI API 요청 / 응답 / 오류 처리
ai_gitgen/formatter.py     길이·형식 검증, 출력 다듬기
```

✏️ 설계 이유 한두 줄 (왜 Git 수집과 AI 호출을 나눴는지 등)

## 8. 테스트

```bash
python -m unittest discover -s tests -t .
```
