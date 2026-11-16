
"""AI API 요청·응답·오류 처리 (Step 5)."""

import json
import os
import urllib.error
import urllib.request

from ai_gitgen import config


class AIClientError(Exception):
    """AI API 호출 관련 오류."""


class MissingApiKeyError(AIClientError):
    """API Key가 없을 때 발생하는 오류."""


def get_api_key(env_name=config.API_KEY_ENV_NAME):
    """환경변수에서 API Key를 읽는다."""
    api_key = os.environ.get(env_name, '').strip()
    if not api_key:
        raise MissingApiKeyError(
            f'{env_name} 환경변수가 설정되지 않았습니다. '
            'PowerShell에서 환경변수를 설정하세요.'
        )
    return api_key


def build_headers(api_key, provider=config.DEFAULT_PROVIDER):
    """AI 제공자에 맞는 요청 헤더를 만든다."""
    if provider == 'anthropic':
        return {
            'x-api-key': api_key,
            'anthropic-version': config.PROVIDERS['anthropic']['api_version'],
            'content-type': 'application/json',
        }
    if provider == 'openai':
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
    raise AIClientError(f'지원하지 않는 AI 제공자: {provider}')


def build_request_body(prompt, model, temperature, max_tokens,
                       provider=config.DEFAULT_PROVIDER):
    """AI에 전송할 요청 본문을 만든다."""
    if provider not in config.PROVIDERS:
        raise AIClientError(f'지원하지 않는 AI 제공자: {provider}')

    body = {
        'model': model,
        'max_tokens': max_tokens,
        'messages': [{'role': 'user', 'content': prompt}],
    }
    if temperature is not None:
        body['temperature'] = temperature
    return body


def extract_text(response_data, provider=config.DEFAULT_PROVIDER):
    """AI 응답에서 생성된 글자를 꺼낸다."""
    try:
        if provider == 'anthropic':
            blocks = response_data['content']
            texts = [
                block['text']
                for block in blocks
                if block.get('type') == 'text'
            ]
            result = '\n'.join(texts).strip()
        elif provider == 'openai':
            result = response_data['choices'][0]['message']['content'].strip()
        else:
            raise AIClientError(f'지원하지 않는 AI 제공자: {provider}')
    except (KeyError, IndexError, TypeError, AttributeError) as error:
        raise AIClientError(
            'AI 응답 형식이 예상과 다릅니다. 제공자와 모델을 확인하세요.'
        ) from error

    if not result:
        raise AIClientError('AI 응답에 생성된 글자가 없습니다.')
    return result


def send_http_request(url, headers, body, timeout):
    """HTTP POST 요청을 보내고 JSON 응답을 받는다."""
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    request = urllib.request.Request(
        url, data=data, headers=headers, method='POST'
    )
    open_request = urllib.request.urlopen
    if (request.type == 'https' and request.host == 'copa.codyssey.kr'
            and urllib.request.getproxies().get('https')
            and not urllib.request.proxy_bypass(request.host)):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        open_request = opener.open

    try:
        with open_request(request, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        detail = ''
        try:
            error_data = json.loads(error.read().decode('utf-8'))
            if isinstance(error_data, dict):
                error_info = error_data.get('error', {})
                if isinstance(error_info, dict):
                    detail = error_info.get('message', '')
                elif isinstance(error_info, str):
                    detail = error_info
                if not detail:
                    detail = error_data.get('detail') or error_data.get('message', '')
        except (ValueError, UnicodeDecodeError):
            pass

        if isinstance(detail, (dict, list)):
            detail = json.dumps(detail, ensure_ascii=False)

        message = f'AI API 요청 실패 (HTTP {error.code})'
        if detail:
            detail = str(detail)
            api_key = request.get_header('X-api-key')
            if api_key is None:
                authorization = request.get_header('Authorization', '')
                api_key = authorization.removeprefix('Bearer ')
            if api_key:
                detail = detail.replace(api_key, '[MASKED]')
            message += f': {detail[:500]}'
        elif (error.headers
              and 'text/html' in error.headers.get('Content-Type', '').lower()):
            message += ': HTML 오류 응답입니다. 프록시 또는 게이트웨이를 확인하세요.'
        raise AIClientError(message) from error

    except urllib.error.URLError as error:
        raise AIClientError(
            f'AI API 네트워크 연결 실패: {error.reason}'
        ) from error
    except TimeoutError as error:
        raise AIClientError(
            'AI API 응답 시간이 초과되었습니다.'
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise AIClientError(
            'AI API 응답을 JSON으로 읽을 수 없습니다.'
        ) from error


def call_ai_api(prompt, model, temperature, max_tokens,
                provider=config.DEFAULT_PROVIDER, api_key=None,
                transport=None):
    """AI API를 한 번 호출하고 생성된 글자를 반환한다."""
    if api_key is None:
        api_key = get_api_key()

    if provider not in config.PROVIDERS:
        raise AIClientError(f'지원하지 않는 AI 제공자: {provider}')

    url = config.PROVIDERS[provider]['url']
    headers = build_headers(api_key, provider)
    body = build_request_body(
        prompt, model, temperature, max_tokens, provider
    )

    sender = transport if transport is not None else send_http_request
    response_data = sender(
        url, headers, body, config.REQUEST_TIMEOUT_SECONDS
    )
    return extract_text(response_data, provider)
