"""AI API 연동 — REST API 요청을 만들고, 보내고, 응답과 오류를 처리한다.

[실습 단계] 🧩 Step 5

[REST API 한 번의 흐름]
    1) API Key 읽기 (환경변수)              get_api_key()
    2) 요청 머리(headers) 만들기             build_headers()
    3) 요청 본문(body, JSON) 만들기          build_request_body()
    4) HTTP POST 로 보내고 JSON 받기         send_http_request()
    5) 응답 JSON 에서 글자만 꺼내기          extract_text()
    1~5 를 순서대로 부르는 함수              call_ai_api()

[실제 API 없이 연습하는 방법 — transport]
    call_ai_api(..., transport=가짜함수) 처럼 "통신 담당 함수"를 바꿔 끼우면
    인터넷·API Key·비용 없이 전체 흐름을 테스트할 수 있다.
    transport 는 다음 모양의 함수다.
        transport(url, headers, body, timeout) -> dict (응답 JSON)
    learning_kit/fake_ai.py 의 FakeTransport 가 그런 가짜 함수다.

[보안 규칙]
    - API Key 값은 코드·로그·오류 메시지에 절대 쓰지 않는다.
    - 키는 환경변수에서만 읽는다.

[자주 쓰는 표준 라이브러리]
    os, json, urllib.request, urllib.error
"""

import json  # noqa: F401  (Step 5 에서 사용합니다)
import os  # noqa: F401
import urllib.error  # noqa: F401
import urllib.request  # noqa: F401

from ai_gitgen import config  # noqa: F401


# ---------------------------------------------------------------------------
# ✅ 구현됨 — 이 모듈 전용 예외(오류) 종류
# ---------------------------------------------------------------------------
class AIClientError(Exception):
    """AI API 호출과 관련된 모든 오류의 부모 예외.

    네트워크 오류, 인증 실패(401), 잘못된 요청(400), 응답 형식 오류 등을
    이 예외로 바꿔서 발생시키면, cli.py 에서는 이것 하나만 잡으면 된다.
    """


class MissingApiKeyError(AIClientError):
    """환경변수에 API Key 가 없을 때 사용하는 예외."""


# ---------------------------------------------------------------------------
# 🧩 Step 5
# ---------------------------------------------------------------------------
def get_api_key(env_name=config.API_KEY_ENV_NAME):
    """환경변수 env_name 에서 API Key 를 읽어 돌려준다.

    - 값이 없거나 공백뿐이면 MissingApiKeyError 를 발생시킨다.
    - 오류 메시지에는 환경변수 "이름"과 설정 예시를 넣는다.
        예) AI_API_KEY 환경변수가 설정되지 않았습니다.
            예) export AI_API_KEY="YOUR_KEY"
    - 키 "값"은 메시지에 넣지 않는다.
    """
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.get_api_key()')


def build_headers(api_key, provider=config.DEFAULT_PROVIDER):
    """제공자 형식에 맞는 HTTP 요청 머리(headers) 사전을 만든다.

    anthropic 형식
        x-api-key         : api_key
        anthropic-version : config.PROVIDERS['anthropic']['api_version']
        content-type      : application/json
    openai 형식
        Authorization     : 'Bearer ' + api_key
        Content-Type      : application/json

    모르는 provider 이름이면 AIClientError 를 발생시킨다.
    (HTTP 헤더 이름은 대소문자를 구분하지 않는다.)
    """
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.build_headers()')


def build_request_body(prompt, model, temperature, max_tokens,
                       provider=config.DEFAULT_PROVIDER):
    """AI API 에 보낼 요청 본문(JSON 으로 바꿀 사전)을 만든다.

    두 제공자가 공통으로 쓰는 모양
        {
            'model': model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [{'role': 'user', 'content': prompt}],
        }

    [선택] temperature 가 None 이면 'temperature' 키를 아예 넣지 않는다.
    (temperature 를 받지 않는 모델을 쓸 때 유용하다.)
    """
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.build_request_body()')


def extract_text(response_data, provider=config.DEFAULT_PROVIDER):
    """응답 JSON(사전)에서 AI 가 만든 글자만 꺼내 돌려준다.

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
    """
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.extract_text()')


def send_http_request(url, headers, body, timeout):
    """실제 HTTP POST 요청을 보내고 응답 JSON 을 사전으로 돌려준다.

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
    """
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.send_http_request()')


def call_ai_api(prompt, model, temperature, max_tokens,
                provider=config.DEFAULT_PROVIDER, api_key=None,
                transport=None):
    """프롬프트를 AI API 에 1번 보내고, 생성된 글자를 돌려준다.

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
    """
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.call_ai_api()')
