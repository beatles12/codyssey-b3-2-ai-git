"""Step 5 연습 테스트 — AI API 요청·응답·오류 처리 (ai_gitgen/ai_client.py)

실행: python -m learning_kit.practice 5

실제 AI API 는 절대 부르지 않는다.
    - transport 테스트: learning_kit.fake_ai.FakeTransport 사용
    - send_http_request 테스트: urllib.request.urlopen 을 가짜로 바꿔 끼움

제공자(provider) 형식
    - 필수 테스트는 config.DEFAULT_PROVIDER 에 고른 제공자 형식만 확인한다.
    - 다른 제공자 형식은 (선택) 테스트다. 공식 미션은 AI API 1개면 충분하다.
    - 이 테스트가 아는 형식은 anthropic, openai 두 가지다.
"""

import io
import json
import os
import unittest
import urllib.error
from unittest import mock

from ai_gitgen import ai_client, config
from learning_kit.fake_ai import FAKE_COMMIT_TEXT, FAKE_PR_TEXT
from learning_kit.fake_ai import FakeTransport, make_anthropic_response
from learning_kit.fake_ai import make_openai_response
from tests.helpers import FAKE_KEY, PracticeTestCase

URL = 'https://api.example.com/v1/test'

SUPPORTED = ('anthropic', 'openai')
PROVIDER = config.DEFAULT_PROVIDER
OTHER = 'openai' if PROVIDER == 'anthropic' else 'anthropic'
COMMIT_FIXTURE = {'anthropic': 'anthropic_commit',
                  'openai': 'openai_commit'}


class FakeHTTPResponse:
    """urlopen 이 돌려주는 응답 객체 흉내."""

    def __init__(self, data=None, raw=None, status=200):
        if raw is None:
            raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self._raw = raw
        self.status = status

    def read(self):
        return self._raw

    def getcode(self):
        return self.status

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def http_error(code, body):
    return urllib.error.HTTPError(
        URL, code, 'error', {}, io.BytesIO(json.dumps(body).encode('utf-8')))


def lower_keys(headers):
    return {str(key).lower(): value for key, value in headers.items()}


def make_response(text, provider):
    if provider == 'openai':
        return make_openai_response(text)
    return make_anthropic_response(text)


def max_tokens_of(body, provider):
    """요청 본문의 출력 길이 상한 값.

    openai 형식은 최신 모델용 이름 max_completion_tokens 도 인정한다.
    """
    if provider == 'openai' and 'max_completion_tokens' in body:
        return body['max_completion_tokens']
    return body['max_tokens']


class ProviderTestCase(PracticeTestCase):
    """제공자별 기대값을 모아 둔 부모 클래스."""

    def setUp(self):
        super().setUp()
        if PROVIDER not in SUPPORTED:
            self.skipTest(f'config.DEFAULT_PROVIDER={PROVIDER!r} 형식은 이 '
                          '연습 테스트가 모릅니다. (anthropic / openai)')

    def check_headers(self, headers, provider):
        headers = lower_keys(headers)
        if provider == 'anthropic':
            self.assertEqual(headers['x-api-key'], FAKE_KEY)
            self.assertEqual(headers['anthropic-version'],
                             config.PROVIDERS['anthropic']['api_version'])
        else:
            self.assertEqual(headers['authorization'], f'Bearer {FAKE_KEY}')
        self.assertIn('application/json', headers['content-type'])

    def load(self, name):
        return json.loads(self.read_data(f'api_responses/{name}.json'))

    def bad_shapes(self, provider):
        if provider == 'anthropic':
            return [{}, {'content': []},
                    {'content': [{'type': 'thinking', 'thinking': ''}]},
                    self.load('anthropic_error_401')]
        return [{}, {'choices': []}, {'error': {'message': 'bad'}}]


class GetApiKeyTest(PracticeTestCase):

    def test_reads_from_environment(self):
        """환경변수 AI_API_KEY 값을 읽어 온다"""
        os.environ['AI_API_KEY'] = FAKE_KEY
        self.assertEqual(ai_client.get_api_key(), FAKE_KEY)

    def test_missing_key_raises(self):
        """환경변수가 없으면 MissingApiKeyError, 메시지에 AI_API_KEY 안내"""
        with self.assertRaises(ai_client.MissingApiKeyError) as context:
            ai_client.get_api_key()
        self.assertIn('AI_API_KEY', str(context.exception))

    def test_blank_key_raises(self):
        """공백뿐인 값도 '설정 안 됨'으로 본다"""
        os.environ['AI_API_KEY'] = '   '
        with self.assertRaises(ai_client.MissingApiKeyError):
            ai_client.get_api_key()

    def test_custom_env_name(self):
        """다른 환경변수 이름도 읽을 수 있다 (env_name 매개변수)"""
        os.environ['B3_TEST_KEY_NAME'] = FAKE_KEY
        self.assertEqual(ai_client.get_api_key('B3_TEST_KEY_NAME'), FAKE_KEY)


class HeadersTest(ProviderTestCase):

    def test_default_provider_headers(self):
        """기본 제공자 형식의 인증 헤더와 content-type 을 만든다"""
        self.check_headers(ai_client.build_headers(FAKE_KEY, PROVIDER),
                           PROVIDER)

    def test_optional_other_provider_headers(self):
        """(선택) 다른 제공자 형식의 헤더도 만든다"""
        self.check_headers(ai_client.build_headers(FAKE_KEY, OTHER), OTHER)

    def test_unknown_provider(self):
        """모르는 제공자 이름은 AIClientError"""
        with self.assertRaises(ai_client.AIClientError):
            ai_client.build_headers(FAKE_KEY, 'no-such-provider')


class RequestBodyTest(ProviderTestCase):

    def test_common_body_shape(self):
        """model / max_tokens / temperature / messages 가 정확히 들어간다"""
        body = ai_client.build_request_body('안녕', 'm-1', 0.3, 200, PROVIDER)
        self.assertEqual(body['model'], 'm-1')
        self.assertEqual(max_tokens_of(body, PROVIDER), 200)
        self.assertEqual(body['temperature'], 0.3)
        self.assertEqual(body['messages'],
                         [{'role': 'user', 'content': '안녕'}])

    def test_body_is_json_serializable(self):
        """본문을 JSON 문자열로 바꿀 수 있다 (한글 포함)"""
        body = ai_client.build_request_body('한글 프롬프트', 'm', 0.5, 10,
                                            PROVIDER)
        self.assertIn('한글 프롬프트', json.dumps(body, ensure_ascii=False))

    def test_optional_temperature_none_is_omitted(self):
        """(선택) temperature=None 이면 'temperature' 키를 넣지 않는다"""
        body = ai_client.build_request_body('x', 'm', None, 10, PROVIDER)
        self.assertNotIn('temperature', body)


class ExtractTextTest(ProviderTestCase):

    def test_default_provider_response(self):
        """기본 제공자 응답에서 글자만 꺼낸다 (anthropic: thinking 블록 건너뛰기)"""
        data = self.load(COMMIT_FIXTURE[PROVIDER])
        self.assertEqual(ai_client.extract_text(data, PROVIDER),
                         FAKE_COMMIT_TEXT)

    def test_default_provider_pr_response(self):
        """PR 초안 응답도 꺼낼 수 있다"""
        data = make_response(FAKE_PR_TEXT, PROVIDER)
        self.assertEqual(ai_client.extract_text(data, PROVIDER), FAKE_PR_TEXT)

    def test_strips_whitespace(self):
        """앞뒤 공백·빈 줄을 정리한다"""
        data = make_response('\n  feat: x  \n\n', PROVIDER)
        self.assertEqual(ai_client.extract_text(data, PROVIDER), 'feat: x')

    def test_unexpected_shapes_raise_client_error(self):
        """모양이 다르거나 글자가 없으면 KeyError 가 아닌 AIClientError"""
        for data in self.bad_shapes(PROVIDER):
            with self.subTest(data=data):
                with self.assertRaises(ai_client.AIClientError):
                    ai_client.extract_text(data, PROVIDER)

    def test_optional_anthropic_multiple_text_blocks(self):
        """(선택) anthropic: text 블록이 여러 개면 모두 이어 붙인다"""
        data = {'content': [{'type': 'text', 'text': 'feat: 첫째'},
                            {'type': 'text', 'text': '- 둘째'}]}
        text = ai_client.extract_text(data, 'anthropic')
        self.assertIn('feat: 첫째', text)
        self.assertIn('- 둘째', text)

    def test_optional_other_provider_response(self):
        """(선택) 다른 제공자 응답도 꺼내고, 모양이 다르면 AIClientError"""
        data = self.load(COMMIT_FIXTURE[OTHER])
        self.assertEqual(ai_client.extract_text(data, OTHER),
                         FAKE_COMMIT_TEXT)
        for bad in self.bad_shapes(OTHER):
            with self.assertRaises(ai_client.AIClientError):
                ai_client.extract_text(bad, OTHER)


class SendHttpRequestTest(PracticeTestCase):

    def test_success_returns_dict(self):
        """성공하면 응답 JSON 을 사전(dict)으로 돌려준다"""
        data = self.read_data('api_responses/anthropic_commit.json')
        fake = FakeHTTPResponse(raw=data.encode('utf-8'))
        with mock.patch('urllib.request.urlopen',
                        return_value=fake) as urlopen:
            result = ai_client.send_http_request(
                URL, {'x-api-key': FAKE_KEY}, {'prompt': '한글'}, 5)
        self.assertEqual(result, json.loads(data))
        self.assertEqual(urlopen.call_count, 1)

    def test_sends_post_with_json_body(self):
        """POST 방식으로, 본문을 JSON(UTF-8 바이트)으로 보낸다"""
        fake = FakeHTTPResponse({'ok': True})
        with mock.patch('urllib.request.urlopen',
                        return_value=fake) as urlopen:
            ai_client.send_http_request(URL, {'x-api-key': FAKE_KEY},
                                        {'prompt': '한글'}, 5)
        args, kwargs = urlopen.call_args
        request = args[0]
        payload = getattr(request, 'data', None)
        if payload is None:
            payload = kwargs.get('data', args[1] if len(args) > 1 else None)
        self.assertEqual(json.loads(payload.decode('utf-8')),
                         {'prompt': '한글'})
        self.assertEqual(request.get_method(), 'POST')
        sent = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(sent.get('x-api-key'), FAKE_KEY)

    def test_http_401_becomes_client_error(self):
        """HTTP 401(인증 실패)은 상태 코드가 들어간 AIClientError"""
        error = http_error(401, {'type': 'error', 'error': {
            'type': 'authentication_error', 'message': 'invalid x-api-key'}})
        with mock.patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaises(ai_client.AIClientError) as context:
                ai_client.send_http_request(URL, {}, {}, 5)
        self.assertIn('401', str(context.exception))

    def test_network_error_becomes_client_error(self):
        """네트워크 오류(URLError)는 원인이 들어간 AIClientError"""
        error = urllib.error.URLError('Name or service not known')
        with mock.patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaises(ai_client.AIClientError) as context:
                ai_client.send_http_request(URL, {}, {}, 5)
        self.assertIn('Name or service not known', str(context.exception))

    def test_timeout_becomes_client_error(self):
        """시간 초과(TimeoutError)도 AIClientError"""
        with mock.patch('urllib.request.urlopen',
                        side_effect=TimeoutError('timed out')):
            with self.assertRaises(ai_client.AIClientError):
                ai_client.send_http_request(URL, {}, {}, 5)

    def test_invalid_json_becomes_client_error(self):
        """응답이 JSON 이 아니면 AIClientError"""
        fake = FakeHTTPResponse(raw=b'<html>Bad Gateway</html>')
        with mock.patch('urllib.request.urlopen', return_value=fake):
            with self.assertRaises(ai_client.AIClientError):
                ai_client.send_http_request(URL, {}, {}, 5)

    def test_optional_error_message_from_api(self):
        """(선택) HTTP 오류 메시지에 API 가 알려 준 원인도 넣는다"""
        error = http_error(401, {'type': 'error', 'error': {
            'type': 'authentication_error', 'message': 'invalid x-api-key'}})
        with mock.patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaises(ai_client.AIClientError) as context:
                ai_client.send_http_request(URL, {}, {}, 5)
        self.assertIn('invalid x-api-key', str(context.exception))


class CallAiApiTest(ProviderTestCase):

    def call(self, **kwargs):
        options = {'prompt': '커밋 메시지를 만들어 줘', 'model': 'm-1',
                   'temperature': 0.2, 'max_tokens': 300,
                   'provider': PROVIDER}
        options.update(kwargs)
        return ai_client.call_ai_api(**options)

    def test_returns_generated_text(self):
        """가짜 AI 응답에서 글자를 꺼내 돌려준다"""
        fake = FakeTransport()
        text = self.call(api_key=FAKE_KEY, transport=fake)
        self.assertEqual(text, FAKE_COMMIT_TEXT)

    def test_calls_transport_exactly_once(self):
        """AI 호출(transport)은 정확히 1번이다 (비용 관리)"""
        fake = FakeTransport()
        self.call(api_key=FAKE_KEY, transport=fake)
        self.assertEqual(fake.call_count, 1)

    def test_sends_correct_request(self):
        """올바른 주소·헤더·본문·timeout 으로 보낸다"""
        fake = FakeTransport()
        self.call(api_key=FAKE_KEY, transport=fake)
        call = fake.calls[0]
        self.assertEqual(call['url'], config.PROVIDERS[PROVIDER]['url'])
        self.check_headers(call['headers'], PROVIDER)
        self.assertEqual(call['body']['messages'][0]['content'],
                         '커밋 메시지를 만들어 줘')
        self.assertEqual(max_tokens_of(call['body'], PROVIDER), 300)
        self.assertEqual(call['timeout'], config.REQUEST_TIMEOUT_SECONDS)

    def test_reads_key_from_environment(self):
        """api_key 를 안 주면 환경변수에서 읽는다"""
        os.environ['AI_API_KEY'] = FAKE_KEY
        fake = FakeTransport()
        self.call(transport=fake)
        self.check_headers(fake.calls[0]['headers'], PROVIDER)

    def test_missing_key_never_calls_api(self):
        """API Key 가 없으면 AI 를 부르지 않고 MissingApiKeyError"""
        fake = FakeTransport()
        with self.assertRaises(ai_client.MissingApiKeyError):
            self.call(transport=fake)
        self.assertEqual(fake.call_count, 0)

    def test_transport_error_is_client_error(self):
        """통신 중 AIClientError 가 나면 그대로 AIClientError 로 전달된다"""
        error = ai_client.AIClientError('AI API 요청 실패 (HTTP 401)')
        with self.assertRaises(ai_client.AIClientError):
            self.call(api_key=FAKE_KEY, transport=FakeTransport(error=error))

    def test_default_transport_uses_send_http_request(self):
        """transport 를 안 주면 send_http_request(urlopen)를 쓴다"""
        data = self.read_data(f'api_responses/{COMMIT_FIXTURE[PROVIDER]}.json')
        fake = FakeHTTPResponse(raw=data.encode('utf-8'))
        with mock.patch('urllib.request.urlopen',
                        return_value=fake) as urlopen:
            text = self.call(api_key=FAKE_KEY)
        self.assertEqual(text, FAKE_COMMIT_TEXT)
        self.assertEqual(urlopen.call_count, 1)

    def test_optional_other_provider(self):
        """(선택) provider 를 바꾸면 그 제공자 주소로 보내고 응답을 읽는다"""
        fake = FakeTransport()
        text = self.call(api_key=FAKE_KEY, transport=fake, provider=OTHER)
        self.assertEqual(fake.calls[0]['url'], config.PROVIDERS[OTHER]['url'])
        self.assertEqual(text, FAKE_COMMIT_TEXT)


if __name__ == '__main__':
    unittest.main()
