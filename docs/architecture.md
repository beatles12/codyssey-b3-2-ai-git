# B3-2 아키텍처 (구조 · 데이터 흐름 · 설계 이유 · 한계)

> CODYSSEY 코딩 가이드라인 7절에 따라 구조와 설계를 코드 밖 문서로 정리했습니다.
> 함수별 상세 명세는 [`docs/modules/`](modules/) 의 모듈 문서를, 그림은 교재
> [`B3-2_STUDY_GUIDE.html`](B3-2_STUDY_GUIDE.html) 2·6·7·8절을 보세요.
> 🧩 표시는 학습자가 구현할 부분이며, 이 문서는 "무엇을 어디에 두는가"만 정합니다.

## 1. 모듈과 책임

| 모듈 | 한 가지 책임 | 구분 (가이드라인 3절) | 문서 | 상태 |
|---|---|---|---|---|
| `main.py` | 프로그램 시작, 학습용 TODO 안내 | 진입점 | [main.md](modules/main.md) | ✅ |
| `ai_gitgen/config.py` | 규칙 숫자·기본값 보관 | 설정 | [config.md](modules/config.md) | ✅ |
| `ai_gitgen/cli.py` | 명령줄 해석, 흐름 지휘, 공통 예외 처리 | 사용자 입력 | [cli.md](modules/cli.md) | 🧩 Step 1·7 |
| `ai_gitgen/git_collector.py` | git status / diff 수집 | 로직 (로컬) | [git_collector.md](modules/git_collector.md) | 🧩 Step 2 |
| `ai_gitgen/safety.py` | 민감정보 마스킹, (선택) 전송 제한 | 로직 | [safety.md](modules/safety.md) | 🧩 Step 3 |
| `ai_gitgen/prompt_builder.py` | 프롬프트 문자열 구성 | 로직 (순수 함수) | [prompt_builder.md](modules/prompt_builder.md) | 🧩 Step 4 |
| `ai_gitgen/ai_client.py` | REST API 요청·응답·오류 변환 | 외부 연동 | [ai_client.md](modules/ai_client.md) | 🧩 Step 5 |
| `ai_gitgen/formatter.py` | 길이·형식 검증, 출력 문자열 | 로직 (순수 함수) | [formatter.md](modules/formatter.md) | 🧩 Step 6 |

이 미션에는 저장 로직(파일·DB)과 별도 데이터 모델이 없습니다. 데이터는 문자열·목록·사전으로만 오갑니다.

학습 지원 코드(`learning_kit/`, `tests/`, `practice_data/`)는 미션 코드와 분리되어 있고, 미션 코드는 이들을 import 하지 않습니다.

## 2. 데이터 흐름과 호출 관계 (commit 기준)

```text
터미널 ─ python main.py commit [옵션]
  main.run()                                   @show_todo_hint (학습 지원)
  └─ cli.main(argv, cwd, transport)            @공통 예외 데코레이터 (Step 7 에서 학습자가 작성)
     ├─ build_parser().parse_args(argv)        → Namespace
     ├─ validate_options(args)                 → 문제 목록 (있으면 [ERROR], 종료 2)
     └─ run_commit(args, cwd, transport)
        ├─ git_collector.is_git_repository     → bool
        ├─ git_collector.get_changed_files     → [{'code', 'path'}]   (없으면 [INFO], 종료 0)
        ├─ git_collector.get_diff              → diff 문자열
        ├─ safety.apply_safe_mode              → 안전한 diff 문자열
        ├─ prompt_builder.build_commit_prompt  → 프롬프트 문자열
        ├─ ai_client.call_ai_api               → AI 가 쓴 글 (HTTP 1회)
        │  └─ get_api_key → build_headers → build_request_body → transport → extract_text
        ├─ formatter.split_title_body / shorten_title / validate_commit_message
        └─ print(formatter.format_commit_output(...))  → 종료 0
```

`pr` 은 같은 뼈대에 `get_current_branch`, `build_pr_prompt`, `validate_pr_title/body`, `format_pr_output` 이 쓰입니다.

| 단계 | 데이터 모양 |
|---|---|
| git 출력 | `str` |
| 정리된 변경 | `list[dict]` + `str` |
| 프롬프트 | `str` |
| HTTP 요청 | 헤더 `dict` + 본문 `dict` → UTF-8 `bytes` |
| HTTP 응답 | `dict` (JSON) |
| 최종 출력 | `str` → `print` |

## 3. 예외 처리 설계 (가이드라인 5·6절)

- 하위 계층은 원인이 분명한 예외를 raise 합니다: `GitCommandError`, `AIClientError`(키 없음은 `MissingApiKeyError`).
- 공통 예외는 진입점 `cli.main()` 에 붙인 데코레이터 **한 곳**에서 `[ERROR]` + 원인 + 해결 힌트로 바꾸고 종료 코드 1 을 돌려줍니다.
- 옵션 오류는 예외가 아니라 사전 검증(`validate_options`) 결과로 처리합니다 (종료 코드 2).
- "변경 사항 없음"은 오류가 아니므로 정상 종료(0)입니다.
- 국소 예외 처리를 허용한 곳과 이유는 각 모듈 문서의 "국소 예외 처리" 표에 있습니다 (`git_collector.md`, `ai_client.md`).
- `main.py` 의 `show_todo_hint` 는 학습 중 `NotImplementedError` 만 안내하는 학습 지원 데코레이터입니다.

## 4. 설계 선택 이유

| 선택 | 이유 |
|---|---|
| Git 수집과 AI 호출 분리 | 실패 원인이 다르고(로컬 vs 네트워크), AI 없이 Git 부분만 테스트 가능, 제공자를 바꿔도 Git 코드는 그대로 |
| 프롬프트와 출력 다듬기 분리 | 프롬프트는 "부탁", formatter 는 "검사". AI 가 부탁을 어길 수 있으므로 검사가 따로 필요 |
| API 파라미터를 CLI 옵션으로 | 코드 수정 없이 같은 조건 반복(재현성)·값만 바꾼 비교 실험 가능 |
| 규칙 숫자를 `config.py` 에 모음 | 규칙이 바뀌면 한 곳만 수정 |
| `transport` 매개변수 | 실제 API·키·비용 없이 전체 흐름을 자동 테스트 |
| 표준 라이브러리만 사용 | REST API 요청 과정을 직접 이해, 설치 문제 없음 |
| 공통 예외 데코레이터 | 같은 try/except 반복을 없애고 오류 메시지 형식을 한 곳에서 관리 |

## 5. 알려진 한계와 개선 방향

| 한계 | 개선 방향 |
|---|---|
| 새 파일(untracked)은 diff 에 내용이 없음 → AI 는 파일 이름만 앎 | `git add -N` 안내 또는 새 파일 내용 일부 첨부 |
| 큰 diff 는 잘라서 보내면(선택 B) 요약이 일부만 반영됨 | 파일별 요약 후 합치기, 중요 파일 우선 |
| 정규식 마스킹은 모양이 정해진 비밀만 찾음 | 패턴 설정 파일·허용 목록 (보너스 3) |
| AI 결과는 사실과 다를 수 있음 (특히 Why, How to Test) | 사람 검토 필수, 팀 템플릿·컨벤션 반영 (보너스 2) |
| 제공자 형식 2종만 준비 | 제공자별 어댑터를 `PROVIDERS` 에 추가 |
| 모델마다 temperature·max_tokens 지원이 다름 | 모델별 허용 파라미터 표를 설정으로 관리 (`config.md` 의 주의사항) |
| 일시 오류(429, 5xx) 재시도 없음 | 호출 상한(1~2회) 안에서 1회 재시도 |
| 비용 추정 없음 | 응답의 `usage` 토큰 수를 로그로 출력 |
