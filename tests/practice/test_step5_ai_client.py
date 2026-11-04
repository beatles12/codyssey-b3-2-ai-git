"""Step 5 연습 테스트 — AI API 요청·응답·오류 처리 (ai_gitgen/ai_client.py)

실행: python -m learning_kit.practice 5

실제 AI API 는 절대 부르지 않는다.
    - transport 테스트: learning_kit.fake_ai.FakeTransport 사용
    - send_http_request 테스트: urllib.request.urlopen 을 가짜로 바꿔 끼움
"""

import io
import json
import os
import unittest
import urllib.error
from unittest import mock

from ai_gitgen import ai_client, config
from learning_kit.fake_ai import FAKE_COMMIT_TEXT, FAKE_PR_TEXT
from learning_kit.fake_ai import FakeTransport
from tests.helpers import FAKE_KEY, PracticeTestCase

URL = 'https://api.example.com/v1/test'


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


class HeadersTest(PracticeTestCase):

    def test_anthropic_headers(self):
        """anthropic: x-api-key, anthropic-version, content-type"""
        headers = lower_keys(ai_client.build_headers(FAKE_KEY, 'anthropic'))
        self.assertEqual(headers['x-api-key'], FAKE_KEY)
        self.assertEqual(headers['anthropic-version'],
                         config.PROVIDERS['anthropic']['api_version'])
        self.assertIn('application/json', headers['content-type'])

    def test_openai_headers(self):
        """openai: Authorization: Bearer <키>"""
        headers = lower_keys(ai_client.build_headers(FAKE_KEY, 'openai'))
        self.assertEqual(headers['authorization'], f'Bearer {FAKE_KEY}')
        self.assertIn('application/json', headers['content-type'])

    def test_unknown_provider(self):
        """모르는 제공자 이름은 AIClientError"""
        with self.assertRaises(ai_client.AIClientError):
            ai_client.build_headers(FAKE_KEY, 'no-such-provider')


class RequestBodyTest(PracticeTestCase):

    def test_common_body_shape(self):
        """model / max_tokens / temperature / messages 가 정확히 들어간다"""
        body = ai_client.build_request_body('안녕', 'm-1', 0.3, 200)
        self.assertEqual(body['model'], 'm-1')
        self.assertEqual(body['max_tokens'], 200)
        self.assertEqual(body['temperature'], 0.3)
        self.assertEqual(body['messages'],
                         [{'role': 'user', 'content': '안녕'}])

    def test_body_is_json_serializable(self):
        """본문을 JSON 문자열로 바꿀 수 있다 (한글 포함)"""
        body = ai_client.build_request_body('한글 프롬프트', 'm', 0.5, 10,
                                            'openai')
        self.assertIn('한글 프롬프트', json.dumps(body, ensure_ascii=False))

    def test_optional_temperature_none_is_omitted(self):
        """(선택) temperature=None 이면 'temperature' 키를 넣지 않는다"""
        body = ai_client.build_request_body('x', 'm', None, 10)
        self.assertNotIn('temperature', body)


class ExtractTextTest(PracticeTestCase):

    def load(self, name):
        return json.loads(self.read_data(f'api_responses/{name}.json'))

    def test_anthropic_skips_thinking_block(self):
        """anthropic 응답: 앞의 thinking 블록을 건너뛰고 text 만 꺼낸다"""
        text = ai_client.extract_text(self.load('anthropic_commit'),
                                      'anthropic')
        self.assertEqual(text, FAKE_COMMIT_TEXT)

    def test_anthropic_pr_response(self):
        """anthropic PR 응답도 꺼낼 수 있다"""
        self.assertEqual(
            ai_client.extract_text(self.load('anthropic_pr'), 'anthropic'),
            FAKE_PR_TEXT)

    def test_anthropic_multiple_text_blocks(self):
        """text 블록이 여러 개면 모두 이어 붙인다"""
        data = {'content': [{'type': 'text', 'text': 'feat: 첫째'},
                            {'type': 'text', 'text': '- 둘째'}]}
        text = ai_client.extract_text(data, 'anthropic')
        self.assertIn('feat: 첫째', text)
        self.assertIn('- 둘째', text)

    def test_openai_response(self):
        """openai 응답: choices[0].message.content 를 꺼낸다"""
        text = ai_client.extract_text(self.load('openai_commit'), 'openai')
        self.assertEqual(text, FAKE_COMMIT_TEXT)

    def test_strips_whitespace(self):
        """앞뒤 공백·빈 줄을 정리한다"""
        data = {'content': [{'type': 'text', 'text': '\n  feat: x  \n\n'}]}
        self.assertEqual(ai_client.extract_text(data, 'anthropic'),
                         'feat: x')

    def test_unexpected_shapes_raise_client_error(self):
        """모양이 다르거나 글자가 없으면 KeyError 가 아닌 AIClientError"""
        cases = [
            ({}, 'anthropic'),
            ({'content': []}, 'anthropic'),
            ({'content': [{'type': 'thinking', 'thinking': ''}]},
             'anthropic'),
            (self.load('anthropic_error_401'), 'anthropic'),
            ({'choices': []}, 'openai'),
            ({}, 'openai'),
        ]
        for data, provider in cases:
            with self.subTest(data=data, provider=provider):
                with self.assertRaises(ai_client.AIClientError):
                    ai_client.extract_text(data, provider)


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


class CallAiApiTest(PracticeTestCase):

    def call(self, **kwargs):
        options = {'prompt': '커밋 메시지를 만들어 줘', 'model': 'm-1',
                   'temperature': 0.2, 'max_tokens': 300}
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
        self.call(api_key=FAKE_KEY, transport=fake, provider='anthropic')
        call = fake.calls[0]
        self.assertEqual(call['url'], config.PROVIDERS['anthropic']['url'])
        self.assertEqual(lower_keys(call['headers'])['x-api-key'], FAKE_KEY)
        self.assertEqual(call['body']['messages'][0]['content'],
                         '커밋 메시지를 만들어 줘')
        self.assertEqual(call['body']['max_tokens'], 300)
        self.assertEqual(call['timeout'], config.REQUEST_TIMEOUT_SECONDS)

    def test_reads_key_from_environment(self):
        """api_key 를 안 주면 환경변수에서 읽는다"""
        os.environ['AI_API_KEY'] = FAKE_KEY
        fake = FakeTransport()
        self.call(transport=fake, provider='anthropic')
        self.assertEqual(lower_keys(fake.calls[0]['headers'])['x-api-key'],
                         FAKE_KEY)

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

    def test_openai_provider(self):
        """provider='openai' 면 openai 주소로 보내고 응답을 읽는다"""
        fake = FakeTransport()
        text = self.call(api_key=FAKE_KEY, transport=fake, provider='openai')
        self.assertEqual(fake.calls[0]['url'],
                         config.PROVIDERS['openai']['url'])
        self.assertEqual(text, FAKE_COMMIT_TEXT)

    def test_default_transport_uses_send_http_request(self):
        """transport 를 안 주면 send_http_request(urlopen)를 쓴다"""
        data = self.read_data('api_responses/anthropic_commit.json')
        fake = FakeHTTPResponse(raw=data.encode('utf-8'))
        with mock.patch('urllib.request.urlopen',
                        return_value=fake) as urlopen:
            text = self.call(api_key=FAKE_KEY, provider='anthropic')
        self.assertEqual(text, FAKE_COMMIT_TEXT)
        self.assertEqual(urlopen.call_count, 1)


if __name__ == '__main__':
    unittest.main()
