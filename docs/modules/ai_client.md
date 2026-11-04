# `ai_gitgen/ai_client.py` — AI API 요청·응답·오류 처리

> 실습 단계: 🧩 Step 5 · 자동 테스트: `tests/practice/test_step5_ai_client.py`
> 코드에는 함수마다 한 줄 설명만 두고, 상세 명세는 이 문서에 둔다 (CODYSSEY 코딩 가이드라인 2·7절).

## 1. 모듈의 성격과 역할

REST API 한 번의 흐름을 담당한다: ① 환경변수에서 키 읽기 ② 헤더 ③ JSON 본문 ④ HTTP POST ⑤ 응답에서 글자 꺼내기. `call_ai_api(..., transport=가짜함수)` 처럼 통신 담당 함수를 바꿔 끼우면 인터넷·키·비용 없이 전체 흐름을 테스트할 수 있다 (`transport(url, headers, body, timeout) -> dict`, 가짜 구현: `learning_kit/fake_ai.py` 의 `FakeTransport`). **보안 규칙**: API Key 값은 코드·로그·오류 메시지에 쓰지 않고, 환경변수에서만 읽는다. 필수 테스트는 `config.DEFAULT_PROVIDER` 형식 1개만 확인하고 다른 제공자 형식은 선택이다.

## 2. 포함된 클래스

| 클래스 | 상태 | 설명 |
|---|---|---|
| `AIClientError` | ✅ 구현됨 | AI API 호출과 관련된 모든 오류의 부모 예외. |
| `MissingApiKeyError` | ✅ 구현됨 | 환경변수에 API Key 가 없을 때 사용하는 예외. |

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `get_api_key()` | 🧩 TODO | 환경변수 env_name 에서 API Key 를 읽어 돌려준다. |
| `build_headers()` | 🧩 TODO | 제공자 형식에 맞는 HTTP 요청 머리(headers) 사전을 만든다. |
| `build_request_body()` | 🧩 TODO | AI API 에 보낼 요청 본문(JSON 으로 바꿀 사전)을 만든다. |
| `extract_text()` | 🧩 TODO | 응답 JSON(사전)에서 AI 가 만든 글자만 꺼내 돌려준다. |
| `send_http_request()` | 🧩 TODO | 실제 HTTP POST 요청을 보내고 응답 JSON 을 사전으로 돌려준다. |
| `call_ai_api()` | 🧩 TODO | 프롬프트를 AI API 에 1번 보내고, 생성된 글자를 돌려준다. |

## 4~6. 함수별 입력·출력과 호출 관계

"명세"는 테스트가 확인하는 약속입니다. 구현 방법(정답)은 들어 있지 않습니다.

### `get_api_key(env_name=config.API_KEY_ENV_NAME)` — 🧩 TODO

- **누가 호출하나**: `call_ai_api()` (또는 `cli.run_*` 에서 미리)
- **다음에 무엇을 호출하나**: `os.environ.get()` (표준)

**명세 (입력 · 출력 · 규칙)**

```text
- 값이 없거나 공백뿐이면 MissingApiKeyError 를 발생시킨다.
- 오류 메시지에는 환경변수 "이름"과 설정 예시를 넣는다.
    예) AI_API_KEY 환경변수가 설정되지 않았습니다.
        예) export AI_API_KEY="YOUR_KEY"
- 키 "값"은 메시지에 넣지 않는다.
```

### `build_headers(api_key, provider=config.DEFAULT_PROVIDER)` — 🧩 TODO

- **누가 호출하나**: `call_ai_api()`
- **다음에 무엇을 호출하나**: `config.PROVIDERS`

**명세 (입력 · 출력 · 규칙)**

```text
필수 테스트는 config.DEFAULT_PROVIDER 형식만 확인한다.
다른 제공자 형식까지 만드는 것은 [선택]이다.

anthropic 형식
    x-api-key         : api_key
    anthropic-version : config.PROVIDERS['anthropic']['api_version']
    content-type      : application/json
openai 형식
    Authorization     : 'Bearer ' + api_key
    Content-Type      : application/json

모르는 provider 이름이면 AIClientError 를 발생시킨다.
(HTTP 헤더 이름은 대소문자를 구분하지 않는다.)
```

### `build_request_body(prompt, model, temperature, max_tokens, provider=config.DEFAULT_PROVIDER)` — 🧩 TODO

- **누가 호출하나**: `call_ai_api()`
- **다음에 무엇을 호출하나**: (사전 만들기)

**명세 (입력 · 출력 · 규칙)**

```text
두 제공자가 공통으로 쓰는 모양
    {
        'model': model,
        'max_tokens': max_tokens,
        'temperature': temperature,
        'messages': [{'role': 'user', 'content': prompt}],
    }

[선택] temperature 가 None 이면 'temperature' 키를 아예 넣지 않는다.
(temperature 를 받지 않는 모델을 쓸 때 유용하다.)

[참고] openai 의 일부 최신(추론) 모델은 max_tokens 대신
max_completion_tokens 라는 이름을 요구한다. openai 형식에서는 테스트가
두 이름을 모두 인정한다. 쓰려는 모델의 공식 문서를 확인하자.
```

### `extract_text(response_data, provider=config.DEFAULT_PROVIDER)` — 🧩 TODO

- **누가 호출하나**: `call_ai_api()`
- **다음에 무엇을 호출하나**: 사전·목록 접근 (기본)

**명세 (입력 · 출력 · 규칙)**

```text
필수 테스트는 config.DEFAULT_PROVIDER 형식만 확인한다. (다른 형식은 선택)

anthropic 응답 모양 (content 는 "목록"이다)
    {'content': [{'type': 'thinking', ...},
                 {'type': 'text', 'text': 'feat: ...'}], ...}
    -> type 이 'text' 인 블록의 text 를 모두 이어 붙인다.
    [함정] content[0] 이 text 가 아닐 수 있다. (thinking 블록 등)
openai 응답 모양
    {'choices': [{'message': {'role': 'assistant',
                              'content': 'feat: ...'}}], ...}

- 꺼낸 글자는 앞뒤 공백을 정리해서 돌려준다.
- 모양이 예상과 다르거나 글자가 비어 있으면 KeyError 등이 그대로
  튀어나가지 않게 AIClientError 로 바꿔서 발생시킨다.
```

### `send_http_request(url, headers, body, timeout)` — 🧩 TODO

- **누가 호출하나**: `call_ai_api()` (transport 가 None 일 때)
- **다음에 무엇을 호출하나**: `json.dumps`, `urllib.request.Request`, `urllib.request.urlopen`, `json.loads` (표준)

**명세 (입력 · 출력 · 규칙)**

```text
- body(사전)는 json.dumps(...).encode('utf-8') 로 바이트로 바꿔 보낸다.
- 반드시 `urllib.request.urlopen(...)` 형태로 호출한다.
  (테스트가 이 함수를 가짜로 바꿔 끼워 실제 통신을 막는다.)

오류 처리 (모두 AIClientError 로 바꿔 발생)
    urllib.error.HTTPError  -> 메시지에 HTTP 상태 코드(예: 401)를 넣는다.
                               가능하면 응답 본문의 오류 설명도 넣는다.
    urllib.error.URLError   -> 네트워크 오류. 원인(reason)을 넣는다.
    TimeoutError            -> 시간 초과
    json.JSONDecodeError    -> 응답이 JSON 이 아님

[주의] HTTPError 는 URLError 의 자식이므로 except 순서가 중요하다.
```

### `call_ai_api(prompt, model, temperature, max_tokens, provider=config.DEFAULT_PROVIDER, api_key=None, transport=None)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr`
- **다음에 무엇을 호출하나**: `get_api_key`, `build_headers`, `build_request_body`, `transport` 또는 `send_http_request`, `extract_text`

**명세 (입력 · 출력 · 규칙)**

```text
매개변수
    api_key   : None 이면 get_api_key() 로 환경변수에서 읽는다.
    transport : None 이면 send_http_request 를 쓴다.
                테스트에서는 가짜 transport 를 넘긴다.

순서
    키 확인 -> 헤더/본문 만들기 -> transport(url, headers, body,
    config.REQUEST_TIMEOUT_SECONDS) 1회 호출 -> extract_text()

테스트가 확인하는 것 (tests/practice/test_step5_ai_client.py)
    - API Key 가 없으면 transport 를 한 번도 부르지 않고
      MissingApiKeyError 가 발생한다.
    - transport 는 정확히 1번 불린다.
    - url 은 config.PROVIDERS[provider]['url'] 이다.
```

### `AIClientError` — ✅ 구현됨

- **사용**: 이 모듈의 함수들이 raise, `cli.main()` 의 공통 예외 데코레이터가 처리

```text
네트워크 오류, 인증 실패(401), 잘못된 요청(400), 응답 형식 오류 등을
이 예외로 바꿔서 발생시키면, cli.py 에서는 이것 하나만 잡으면 된다.
```

### `MissingApiKeyError` — ✅ 구현됨

- **사용**: `get_api_key()` 가 raise

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수·메서드 | `str.strip`, `dict.get`, `isinstance` |
| 표준 라이브러리 | `os`, `json`, `urllib.request`, `urllib.error` |
| 문법/개념 | `class` 상속(예외 계층), `try/except`, `raise ... from`, `with`, 함수를 값으로 넘기기(transport) |
| 프로젝트 코드 | `AIClientError`, `MissingApiKeyError`, 함수 6개, `config.PROVIDERS` |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| `os` | 환경변수 `AI_API_KEY` 읽기 (키를 코드에 쓰지 않기 위해) |
| `json` | 요청 본문 사전 ↔ JSON 문자열/바이트 변환 |
| `urllib.request` | 외부 패키지 없이 HTTP POST 보내기 (REST API 원리를 직접 이해) |
| `urllib.error` | HTTP 상태 오류(`HTTPError`)와 네트워크 오류(`URLError`) 구분 |

## 국소 예외 처리 (가이드라인 5절의 예외적 허용과 이유)

공통 예외는 진입점 `cli.main()` 의 데코레이터에서 한 번에 처리한다. 아래는 하위 계층에서 꼭 필요한 것만 허용한 경우다.

| 함수 | 하는 일 | 이유 |
|---|---|---|
| `send_http_request()` | `HTTPError`/`URLError`/`TimeoutError`/`JSONDecodeError` → `AIClientError` 로 바꿔 raise | 공식 요구 "API 호출 실패 시 오류 원인 포함 메시지" — 상태 코드·원인을 담은 명확한 예외를 올리기 위해 |
| `extract_text()` | `KeyError`/`IndexError`/`TypeError` → `AIClientError` | 응답 모양이 다를 때 사용자에게 Traceback 대신 원인을 보여 주기 위해 |
