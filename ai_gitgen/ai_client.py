"""AI API 요청·응답·오류 처리 (🧩 Step 5). 명세: docs/modules/ai_client.md"""

import json  # noqa: F401  (Step 5 에서 사용합니다)
import os  # noqa: F401
import urllib.error  # noqa: F401
import urllib.request  # noqa: F401

from ai_gitgen import config  # noqa: F401


# ✅ 구현됨 — 이 모듈 전용 예외(오류) 종류
class AIClientError(Exception):
    """AI API 호출과 관련된 모든 오류의 부모 예외."""


class MissingApiKeyError(AIClientError):
    """환경변수에 API Key 가 없을 때 쓰는 예외."""


# 🧩 Step 5
def get_api_key(env_name=config.API_KEY_ENV_NAME):
    """환경변수에서 API Key 를 읽는다. 없거나 공백이면 MissingApiKeyError."""
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.get_api_key()')


def build_headers(api_key, provider=config.DEFAULT_PROVIDER):
    """제공자 형식에 맞는 HTTP 요청 헤더 사전을 만든다."""
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.build_headers()')


def build_request_body(prompt, model, temperature, max_tokens,
                       provider=config.DEFAULT_PROVIDER):
    """AI API 에 보낼 요청 본문 사전을 만든다."""
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.build_request_body()')


def extract_text(response_data, provider=config.DEFAULT_PROVIDER):
    """응답 JSON 에서 AI 가 만든 글자만 꺼낸다. 모양이 다르면 AIClientError."""
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.extract_text()')


def send_http_request(url, headers, body, timeout):
    """HTTP POST 를 보내고 응답 JSON 을 사전으로 돌려준다. 실패는 AIClientError."""
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.send_http_request()')


def call_ai_api(prompt, model, temperature, max_tokens,
                provider=config.DEFAULT_PROVIDER, api_key=None,
                transport=None):
    """프롬프트를 AI API 에 1번 보내고 생성된 글자를 돌려준다."""
    # TODO(Step 5): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 5 - ai_client.call_ai_api()')
