# `ai_gitgen/prompt_builder.py` — 프롬프트 구성

> 실습 단계: 🧩 Step 4 · 자동 테스트: `tests/practice/test_step4_prompt.py`
> 코드에는 함수마다 한 줄 설명만 두고, 상세 명세는 이 문서에 둔다 (CODYSSEY 코딩 가이드라인 2·7절).

## 1. 모듈의 성격과 역할

AI 에게 보낼 요청문(문자열)을 만든다. 미션의 핵심인 "어떤 입력을 주냐"를 담당한다. 받은 결과를 검사하는 `formatter.py` 와 분리한 이유: AI 는 부탁을 100% 지키지 않으므로 "부탁"과 "검사"가 따로 있어야 한다. 이 모듈의 함수는 **순수 함수**로 만든다 — 입력이 같으면 항상 같은 문자열 (시간·난수 금지) → 테스트와 재현 실험이 가능.

## 2. 포함된 클래스

없음.

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `format_file_list()` | 🧩 TODO | 변경 파일 목록을 사람이 읽기 좋은 여러 줄 문자열로 바꾼다. |
| `build_commit_prompt()` | 🧩 TODO | 커밋 메시지 생성을 부탁하는 프롬프트 문자열을 만든다. |
| `build_pr_prompt()` | 🧩 TODO | PR 제목/본문 초안 생성을 부탁하는 프롬프트 문자열을 만든다. |

## 4~6. 함수별 입력·출력과 호출 관계

"명세"는 테스트가 확인하는 약속입니다. 구현 방법(정답)은 들어 있지 않습니다.

### `format_file_list(changed_files)` — 🧩 TODO

- **누가 호출하나**: `build_commit_prompt()`, `build_pr_prompt()`
- **다음에 무엇을 호출하나**: `str.join`, f-string (기본)

**명세 (입력 · 출력 · 규칙)**

```text
입력 예) [{'code': 'M', 'path': 'app.py'}, {'code': '??', 'path': 'a.txt'}]
출력 예)
    - [M] app.py
    - [??] a.txt
빈 목록이면 '(변경 파일 없음)' 같은 안내 문자열을 돌려준다.
```

### `build_commit_prompt(changed_files, diff_text)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`
- **다음에 무엇을 호출하나**: `format_file_list()`, `config.COMMIT_TITLE_*`

**명세 (입력 · 출력 · 규칙)**

```text
반드시 들어가야 할 것 (테스트가 확인)
    - 변경된 모든 파일 경로
    - diff_text 내용 (diff 가 비어 있어도 오류 없이 동작)
    - 커밋 제목 길이 규칙 숫자 (50자 권장 / 최대 72자)

넣으면 좋은 것 (교재 Step 4 힌트 참고)
    - 역할: 너는 무엇을 하는 도우미인가
    - 출력 형식: 첫 줄 제목, 빈 줄, 본문 불릿 1~2개
    - 제목 앞머리 규칙: feat / fix / docs / refactor / test ...
    - 출력 언어: 한국어
    - 하지 말 것: 설명 문장, 코드 블록(```) 감싸기
```

### `build_pr_prompt(changed_files, diff_text, branch_name)` — 🧩 TODO

- **누가 호출하나**: `cli.run_pr`
- **다음에 무엇을 호출하나**: `format_file_list()`, `config.PR_TITLE_MAX`, `config.PR_SECTIONS`

**명세 (입력 · 출력 · 규칙)**

```text
반드시 들어가야 할 것 (테스트가 확인)
    - 변경된 모든 파일 경로, diff_text, branch_name
    - 섹션 이름 'Why', 'What', 'How to Test'
    - PR 제목 최대 길이 숫자 (80)

출력 형식을 정해 두면 받은 뒤 나누기 쉽다. 예)
    첫 줄      : PR 제목 (한 줄)
    그다음 줄부터 : ## Why / ## What / ## How to Test 섹션과 불릿
```

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수·메서드 | `str.join` |
| 표준 라이브러리 | (없음) |
| 문법/개념 | f-string, 여러 줄 문자열 이어 붙이기, 제너레이터 식 |
| 프로젝트 코드 | 함수 3개, `config` 상수 |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| (없음) | 문자열 조립만 하므로 기본 기능으로 충분 |
