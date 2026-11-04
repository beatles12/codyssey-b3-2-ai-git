# `ai_gitgen/cli.py` — 명령줄 처리와 전체 흐름 연결

> 실습 단계: 🧩 Step 1, 7 · 자동 테스트: `tests/practice/test_step1_cli_options.py, tests/practice/test_step7_flow.py`
> 코드에는 함수마다 한 줄 설명만 두고, 상세 명세는 이 문서에 둔다 (CODYSSEY 코딩 가이드라인 2·7절).

## 1. 모듈의 성격과 역할

사용자 입력(명령줄)을 해석하고, 다른 모듈의 함수를 순서대로 불러 결과를 출력하는 **지휘자**다. 사용자 입력 처리(이 모듈)와 로직(git_collector·safety·prompt_builder·formatter), 외부 연동(ai_client)을 분리한다 (가이드라인 3절).

## 2. 포함된 클래스

없음.

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `log()` | ✅ 구현됨 | 머리표([INFO], [DONE], [WARN], [ERROR])를 붙여 한 줄을 출력한다. |
| `build_parser()` | 🧩 TODO | commit / pr 하위 명령과 공통 옵션을 가진 ArgumentParser 를 만든다. |
| `validate_options()` | 🧩 TODO | parse_args 로 얻은 옵션 값이 허용 범위 안에 있는지 검사한다. |
| `run_commit()` | 🧩 TODO | `commit` 명령의 전체 흐름을 실행하고 종료 코드를 돌려준다. |
| `run_pr()` | 🧩 TODO | `pr` 명령의 전체 흐름을 실행하고 종료 코드를 돌려준다. |
| `main()` | 🧩 TODO | 프로그램 시작점. 옵션을 해석하고 commit / pr 흐름으로 보낸다. |

## 4~6. 함수별 입력·출력과 호출 관계

"명세"는 테스트가 확인하는 약속입니다. 구현 방법(정답)은 들어 있지 않습니다.

### `log(level, message)` — ✅ 구현됨

- **누가 호출하나**: `run_commit`, `run_pr`, `main`, 공통 예외 데코레이터
- **다음에 무엇을 호출하나**: `print()` (기본), `sys.stdout`/`sys.stderr` (표준)

**명세 (입력 · 출력 · 규칙)**

```text
예)
    log('INFO', 'AI API 요청 중...')  ->  [INFO] AI API 요청 중...

[ERROR] 는 표준 오류(sys.stderr)로, 나머지는 표준 출력으로 보낸다.
이렇게 나누면 정상 결과와 오류 메시지를 따로 저장하거나 볼 수 있다.
```

### `build_parser()` — 🧩 TODO

- **누가 호출하나**: `main()`
- **다음에 무엇을 호출하나**: `argparse.ArgumentParser`, `add_subparsers`, `add_argument` (표준)

**명세 (입력 · 출력 · 규칙)**

```text
반환값
    argparse.ArgumentParser

만들어야 하는 명령 형태
    python main.py commit [옵션]
    python main.py pr     [옵션]

두 하위 명령에 모두 있어야 하는 옵션 (하위 명령 "뒤"에 쓸 수 있어야 함)
    --model        문자열, 기본값 config.DEFAULT_MODEL
    --temperature  실수(float), 기본값 config.DEFAULT_TEMPERATURE
    --max-tokens   정수(int),  기본값 config.DEFAULT_MAX_TOKENS
                   (parse_args 결과에서는 args.max_tokens 로 읽힌다)
    --safe-mode    켜기/끄기(store_true), 기본값 False
    --dry-run      켜기/끄기(store_true), 기본값 False   [권장·선택]
                   AI 를 부르지 않고 "보낼 프롬프트"만 보여 주는 모드

parse_args 결과(Namespace)에서 확인하는 값
    args.command      'commit' 또는 'pr'
    args.model, args.temperature, args.max_tokens,
    args.safe_mode, args.dry_run

테스트가 확인하는 것 (tests/practice/test_step1_cli_options.py)
    - 하위 명령 없이 실행하면 SystemExit 이 발생한다.
    - --max-tokens abc 처럼 숫자가 아니면 SystemExit 이 발생한다.
```

### `validate_options(args)` — 🧩 TODO

- **누가 호출하나**: `main()`
- **다음에 무엇을 호출하나**: 비교 연산, `config.TEMPERATURE_*`·`MAX_TOKENS_*`

**명세 (입력 · 출력 · 규칙)**

```text
매개변수
    args : build_parser().parse_args(...) 의 결과

반환값
    list[str] : 문제를 설명하는 한국어 메시지 목록. 문제가 없으면 [].

검사 규칙 (범위 값은 config.py 에 있음)
    - temperature 가 TEMPERATURE_MIN ~ TEMPERATURE_MAX 를 벗어나면
      'temperature' 라는 단어가 들어간 메시지를 추가한다.
    - max_tokens 가 MAX_TOKENS_MIN ~ MAX_TOKENS_LIMIT 를 벗어나면
      'max' 라는 단어가 들어간 메시지를 추가한다. (예: --max-tokens)
    - model 이 빈 문자열이면 'model' 이 들어간 메시지를 추가한다.

왜 필요할까?
    잘못된 값으로 AI API 를 부르면 돈(토큰)과 시간을 쓴 뒤에야
    오류를 알게 된다. 보내기 "전에" 검사하면 비용 없이 막을 수 있다.
```

### `run_commit(args, cwd=None, transport=None)` — 🧩 TODO

- **누가 호출하나**: `main()`
- **다음에 무엇을 호출하나**: `git_collector.*`, `safety.apply_safe_mode`, `prompt_builder.build_commit_prompt`, `ai_client.call_ai_api`, `formatter.*`, `log`

**명세 (입력 · 출력 · 규칙)**

```text
매개변수
    args      : parse_args 결과
    cwd       : Git 명령을 실행할 폴더 (None 이면 현재 폴더)
    transport : 테스트용 가짜 통신 함수. ai_client.call_ai_api() 에
                그대로 넘긴다. (None 이면 실제 HTTP 통신)

반환값 (종료 코드)
    0 : 정상 완료, 또는 "변경 사항이 없습니다" 안내 후 종료
    1 : Git 저장소가 아님 / API Key 없음 / API 호출 실패 등 오류

권장 흐름 (교재의 '커밋 메시지 생성 흐름' 그림 참고)
    1) Git 저장소인지 확인 -> 아니면 [ERROR]
    2) 변경 파일 목록 수집 -> 없으면 [INFO] 변경 사항이 없습니다 ... 후 0
    3) diff 수집 -> 줄 수를 [INFO] 로 출력
    4) --safe-mode 면 마스킹/전송 제한 적용
    5) 커밋용 프롬프트 만들기 (--dry-run 이면 여기서 출력하고 0)
    6) AI API 1회 호출 (호출 횟수를 로그로 출력)
    7) 제목/본문 나누기 -> 길이 규칙 적용 -> 검증 결과는 [WARN]
    8) format_commit_output() 으로 구획을 나눠 출력

테스트가 확인하는 것 (tests/practice/test_step7_flow.py)
    - 변경이 없으면 AI 를 부르지 않는다.
    - API Key 가 없으면 AI 를 부르지 않고 'AI_API_KEY' 를 안내한다.
    - 정상일 때 AI 호출은 정확히 1회다.
    - 출력된 커밋 제목은 72자 이하다.
```

### `run_pr(args, cwd=None, transport=None)` — 🧩 TODO

- **누가 호출하나**: `main()`
- **다음에 무엇을 호출하나**: `run_commit` 과 같고 `get_current_branch`, `build_pr_prompt`, `validate_pr_title/body`, `format_pr_output` 사용

**명세 (입력 · 출력 · 규칙)**

```text
run_commit() 과 거의 같지만 다음이 다르다.
    - 현재 브랜치 이름을 [INFO] 로 출력하고 프롬프트에 넣는다.
    - AI 응답의 첫 줄을 PR 제목, 나머지를 PR 본문으로 쓴다.
    - PR 제목은 80자 이하, 본문은 Why / What / How to Test 섹션과
      섹션마다 1개 이상의 불릿(- )이 있어야 한다.
    - format_pr_output() 으로 구획을 나눠 출력한다.

길이/형식 규칙을 지키는 방법은 둘 중 하나를 고른다 (공식 요구사항).
    (가) 후처리: 프로그램이 직접 자르고 다듬는다. (추가 비용 없음)
    (나) 재생성: 규칙을 어기면 1번만 더 요청한다. (호출 최대 2회)
```

### `main(argv=None, cwd=None, transport=None)` — 🧩 TODO

- **누가 호출하나**: `main.py` 의 `run()`, Step 7 테스트, `learning_kit/demo.py`
- **다음에 무엇을 호출하나**: `build_parser().parse_args`, `validate_options`, `run_commit` 또는 `run_pr`

**명세 (입력 · 출력 · 규칙)**

```text
매개변수
    argv      : 옵션 목록 (None 이면 실제 명령줄 sys.argv[1:] 사용)
                예) ['commit', '--temperature', '0.2']
    cwd       : run_commit / run_pr 에 그대로 넘긴다.
    transport : run_commit / run_pr 에 그대로 넘긴다.

반환값 (종료 코드)
    run_commit / run_pr 의 반환값.
    validate_options() 가 문제를 찾으면 [ERROR] 로 알리고 2 를 반환
    (AI 는 부르지 않는다).
```

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수·메서드 | `print`, `float`, `int` |
| 표준 라이브러리 | `argparse`, `sys`, (데코레이터를 만든다면) `functools` |
| 문법/개념 | 데코레이터(`@`), `try/except`, 기본값 `None` 매개변수, 함수를 값으로 넘기기(transport) |
| 프로젝트 코드 | `log()` 외 함수 6개, 모든 ai_gitgen 모듈 |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| `argparse` | 하위 명령(commit/pr)과 옵션(--model 등), 타입 변환·오류 안내를 표준 방식으로 처리 |
| `sys` | `[ERROR]` 는 표준 오류(stderr), 나머지는 표준 출력(stdout)으로 나누기 |
| `functools` | (선택) 공통 예외 데코레이터에 `functools.wraps` — 원래 함수 이름·매개변수가 유지되어 기본 테스트(함수 약속)가 통과 |

## 예외 처리 설계 (가이드라인 5·6절)

공식 요구 "API 호출 실패 시 오류 원인을 포함한 메시지"와 가이드라인 "공통 예외는 진입점 데코레이터에서 통합,
같은 try/except 반복 금지"를 함께 만족하도록 다음처럼 나눈다.

| 상황 | 처리 위치 | 방법 | 종료 코드 |
|---|---|---|---|
| 옵션 값이 범위 밖 | `main()` | 예외가 아니라 **사전 검증** 결과(`validate_options()` 의 문제 목록)로 `[ERROR]` 출력 | 2 |
| 변경 사항 없음 | `run_commit` / `run_pr` | 오류가 아니므로 `[INFO]` 안내 후 정상 종료 | 0 |
| Git 저장소 아님, git 실패 | 하위 계층이 `GitCommandError` 를 raise | `main()` 에 붙인 **공통 예외 데코레이터** 한 곳에서 `[ERROR]` + 원인 + 해결 힌트 | 1 |
| API Key 없음, HTTP 401/400/429, 네트워크 오류, 응답 모양 다름 | `ai_client` 가 `AIClientError` (또는 `MissingApiKeyError`) 를 raise | 같은 데코레이터에서 처리 | 1 |

- `run_commit` 과 `run_pr` 안에서 같은 `try/except` 를 반복하지 않는다. 예외가 그대로 올라오게 둔다.
- 데코레이터 이름은 역할이 드러나게 짓는다 (예: `handle_cli_errors`). `main()` **위에 한 번만** 붙인다.
- `functools.wraps` 를 쓰면 감싼 뒤에도 `main` 의 이름·매개변수가 유지되어 기본 테스트(함수 약속)가 계속 통과한다.
- 사용자에게는 Traceback 대신 원인과 해결 힌트를 보여 준다. 예) `AI_API_KEY 환경변수가 설정되지 않았습니다.` + `예) export AI_API_KEY="YOUR_KEY"`
- 실제로 구현된 데코레이터 예: `main.py` 의 `show_todo_hint` (학습 지원용, `NotImplementedError` 만 처리).
- `run_commit` 과 `run_pr` 의 공통 부분(변경 수집 → safe-mode → AI 호출)은 공통 함수로 분리하면 중복이 줄어든다 (가이드라인 3절).
