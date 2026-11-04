# `ai_gitgen/safety.py` — 안전 모드 (--safe-mode)

> 실습 단계: 🧩 Step 3 · 자동 테스트: `tests/practice/test_step3_safety.py`
> 코드에는 함수마다 한 줄 설명만 두고, 상세 명세는 이 문서에 둔다 (CODYSSEY 코딩 가이드라인 2·7절).

## 1. 모듈의 성격과 역할

AI 에게 보내기 전에 diff 를 안전하게 만든다. 공식 제약은 (A) 민감 패턴 마스킹 / (B) 일부만 전송 중 **1개 이상**이며, 이 실습은 (A)를 필수, (B)를 선택으로 둔다.

## 2. 포함된 클래스

없음.

모듈 상수:

| 이름 | 상태 | 설명 |
|---|---|---|
| `MASK_TEXT` | ✅ 구현됨 | 가려진 자리에 넣을 글자 `'[MASKED]'` |
| `SENSITIVE_PATTERNS` | 🧩 TODO | (이름, 정규표현식) 튜플 목록. **필수**: `sk-` 로 시작하는 긴 API Key 모양, 이메일. **선택**: `api_key`/`secret`/`token`/`password` 뒤 `=`·`:` 로 이어지는 값(대소문자 무관), 휴대전화 번호(010-1234-5678). 형식은 권장이며 바꿔도 된다 |

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `mask_sensitive()` | 🧩 TODO | text 안의 민감정보를 MASK_TEXT 로 바꾼 새 문자열을 돌려준다. |
| `limit_diff()` | 🧩 TODO | [선택] diff 를 앞에서부터 최대 max_files 개 파일, max_lines 줄로 자른다. |
| `apply_safe_mode()` | 🧩 TODO | enabled 가 True 면 안전 처리를 적용하고, False 면 그대로 둔다. |

## 4~6. 함수별 입력·출력과 호출 관계

"명세"는 테스트가 확인하는 약속입니다. 구현 방법(정답)은 들어 있지 않습니다.

### `mask_sensitive(text)` — 🧩 TODO

- **누가 호출하나**: `apply_safe_mode()`
- **다음에 무엇을 호출하나**: `re.sub()` (표준) — `SENSITIVE_PATTERNS` 를 돌며 적용

**명세 (입력 · 출력 · 규칙)**

```text
- 민감정보가 아닌 부분은 한 글자도 바뀌면 안 된다.
- 예) 'API_KEY = "fake-key-123456"'  ->  'API_KEY = "[MASKED]"'
      'contact: kim@example.com'  ->  'contact: [MASKED]'

힌트: SENSITIVE_PATTERNS 를 돌면서 re.sub() 를 적용한다.
```

### `limit_diff(diff_text, max_files=config.SAFE_MODE_MAX_FILES, max_lines=config.SAFE_MODE_MAX_LINES)` — 🧩 TODO

- **누가 호출하나**: `apply_safe_mode()` (구현한 경우)
- **다음에 무엇을 호출하나**: `str.splitlines(keepends=True)`, `str.startswith`, `''.join` (기본)

**명세 (입력 · 출력 · 규칙)**

```text
공식 제약 (B). 구현하지 않기로 했다면 이 함수는 그대로 두고,
apply_safe_mode() 에서 부르지 않으면 된다.

규칙
    - 파일 하나의 diff 는 'diff --git ' 으로 시작하는 줄부터 시작한다.
    - 파일 수 제한을 먼저 적용하고, 그다음 전체 줄 수를 제한한다.
    - 잘라 낸 내용이 있으면 맨 끝에 안내 줄 1개를 덧붙인다.
      예) '... (safe-mode: 120줄 생략)'
    - 제한보다 작으면 원래 문자열을 그대로 돌려준다.

왜 필요할까?
    diff 가 길수록 AI 요청 비용(토큰)이 커지고, 민감한 파일이 섞일
    가능성도 커진다. 보내는 양에 상한을 두면 둘 다 줄일 수 있다.
```

### `apply_safe_mode(diff_text, enabled=True)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr`
- **다음에 무엇을 호출하나**: `mask_sensitive()`, (선택) `limit_diff()`

**명세 (입력 · 출력 · 규칙)**

```text
- 필수: mask_sensitive() 로 마스킹 (A)
- 선택: limit_diff() 를 구현했다면 전송 제한 (B) 도 적용

반환값
    str : AI 에게 보낼 diff 텍스트
```

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수·메서드 | `str.splitlines`, `str.startswith`, `str.join`, `len` |
| 표준 라이브러리 | `re` |
| 문법/개념 | 정규표현식 문자열 `r'...'`, `for`, 기본값 매개변수 |
| 프로젝트 코드 | `MASK_TEXT`, `SENSITIVE_PATTERNS`, 함수 3개, `config.SAFE_MODE_*` |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| `re` | "API Key 모양", "이메일 모양"처럼 글자의 **모양**으로 찾아 바꾸려면 정규표현식이 필요 |
