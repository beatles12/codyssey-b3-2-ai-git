# `ai_gitgen/formatter.py` — 출력 형식 검증과 다듬기

> 실습 단계: 🧩 Step 6 · 자동 테스트: `tests/practice/test_step6_formatter.py`
> 코드에는 함수마다 한 줄 설명만 두고, 상세 명세는 이 문서에 둔다 (CODYSSEY 코딩 가이드라인 2·7절).

## 1. 모듈의 성격과 역할

AI 가 만든 글을 공식 규칙(커밋 제목 50자 권장·최대 72자, PR 제목 최대 80자, PR 본문 Why/What/How to Test + 섹션별 불릿)에 맞는지 검사하고, 구분선·헤더로 구획을 나눈 출력 문자열을 만든다. AI 는 형식을 가끔 어기므로 받은 뒤 프로그램이 다시 확인한다. `len()` 은 글자 수를 센다 (`len('가나다') == 3`). 제목 길이 검사처럼 커밋·PR 에서 반복되는 검증은 공통 함수로 묶어도 좋다 (가이드라인 3절).

## 2. 포함된 클래스

없음.

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `split_title_body()` | 🧩 TODO | AI 응답 글을 (제목, 본문) 두 부분으로 나눈다. |
| `shorten_title()` | 🧩 TODO | 제목이 max_length 글자보다 길면 max_length 글자 이하로 줄인다. |
| `validate_commit_message()` | 🧩 TODO | 커밋 메시지가 규칙을 지키는지 검사해 문제 목록을 돌려준다. |
| `validate_pr_title()` | 🧩 TODO | PR 제목 문제 목록을 돌려준다. (빈 제목, 80자 초과, 여러 줄) |
| `validate_pr_body()` | 🧩 TODO | PR 본문 문제 목록을 돌려준다. 문제가 없으면 []. |
| `format_commit_output()` | 🧩 TODO | 커밋 메시지를 구획이 나뉜 터미널 출력용 문자열로 만든다. |
| `format_pr_output()` | 🧩 TODO | PR 제목과 본문을 구획이 나뉜 터미널 출력용 문자열로 만든다. |

## 4~6. 함수별 입력·출력과 호출 관계

"명세"는 테스트가 확인하는 약속입니다. 구현 방법(정답)은 들어 있지 않습니다.

### `split_title_body(text)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr` (검증 함수 안에서 써도 됨)
- **다음에 무엇을 호출하나**: `str.strip`, `str.splitlines` (기본)

**명세 (입력 · 출력 · 규칙)**

```text
규칙
    - 제목 : 비어 있지 않은 첫 줄 (앞뒤 공백 제거)
    - 본문 : 그 아래 나머지 전부 (앞뒤 빈 줄/공백 제거). 없으면 ''.
    - text 가 비어 있으면 ('', '')

예) 'feat: 검색 추가\n\n- search.py 추가'
    -> ('feat: 검색 추가', '- search.py 추가')

[선택] AI 가 ``` 로 감싸서 답하는 경우도 있다. ``` 줄을 무시하면
더 튼튼해진다.
```

### `shorten_title(title, max_length)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr` (후처리를 고른 경우)
- **다음에 무엇을 호출하나**: `len`, 슬라이싱 (기본)

**명세 (입력 · 출력 · 규칙)**

```text
- 짧으면 그대로 돌려준다.
- 줄였다는 표시('...' 또는 '…')를 붙여도 되지만, 붙인 뒤에도
  전체 길이는 max_length 이하여야 한다.
```

### `validate_commit_message(message, changed_paths=None)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`
- **다음에 무엇을 호출하나**: `split_title_body()`, `config.COMMIT_TITLE_MAX`

**명세 (입력 · 출력 · 규칙)**

```text
반환값
    list[str] : 문제 설명 목록. 문제가 없으면 [].

규칙
    - 제목이 비어 있으면 문제
    - 제목이 config.COMMIT_TITLE_MAX(72)자를 넘으면 문제
      (메시지에 '72' 를 넣어 무엇이 기준인지 알려 준다)
    - 본문이 있는데, 불릿 줄('- ' 또는 '* ' 로 시작)이 하나도 없고
      changed_paths 중 어떤 파일 이름도 언급하지 않으면 문제
      (공식 요약 품질 최소 기준)
```

### `validate_pr_title(title)` — 🧩 TODO

- **누가 호출하나**: `cli.run_pr`
- **다음에 무엇을 호출하나**: `config.PR_TITLE_MAX`

### `validate_pr_body(body)` — 🧩 TODO

- **누가 호출하나**: `cli.run_pr`
- **다음에 무엇을 호출하나**: `config.PR_SECTIONS`

**명세 (입력 · 출력 · 규칙)**

```text
규칙
    - config.PR_SECTIONS 의 각 섹션마다 '#' 으로 시작하는 헤더 줄이
      있어야 한다. 예) '## Why', '### What', '## How to Test'
      (헤더 글자가 섹션 이름으로 "시작"하면 인정: '## Why (변경 배경)')
    - 각 섹션 아래(다음 헤더 전까지)에 불릿 줄이 1개 이상 있어야 한다.
    - 문제 메시지에는 섹션 이름을 넣는다. 예) 'How to Test 섹션이 없습니다'
```

### `format_commit_output(message)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`
- **다음에 무엇을 호출하나**: `config.SEPARATOR`

**명세 (입력 · 출력 · 규칙)**

```text
형식 (테스트가 확인)
    --- Commit Message ---     <- 'Commit Message' 가 들어간 헤더 줄
    feat: ...                  <- 헤더 다음의 첫 글자 줄 = 커밋 제목
    (본문)
    ----------------------     <- 구분선 ('-' 3개 이상으로 된 줄)
```

### `format_pr_output(title, body)` — 🧩 TODO

- **누가 호출하나**: `cli.run_pr`
- **다음에 무엇을 호출하나**: `config.SEPARATOR`

**명세 (입력 · 출력 · 규칙)**

```text
형식 (테스트가 확인)
    --- PR Title ---           <- 'PR Title' 헤더 다음 첫 줄 = 제목
    feat: ...
    --- PR Body ---            <- 'PR Body' 헤더 다음 = 본문
    ## Why
    - ...
    ----------------------     <- 구분선
```

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수·메서드 | `len`, `str.splitlines`, `str.strip`, `str.lstrip`, `str.startswith`, 슬라이싱 |
| 표준 라이브러리 | (없음) |
| 문법/개념 | 튜플 반환·언패킹 `(제목, 본문)`, `for`, 조건문 |
| 프로젝트 코드 | 함수 7개, `config` 상수 |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| (없음) | 문자열 검사·조립만 하므로 기본 기능으로 충분 |
