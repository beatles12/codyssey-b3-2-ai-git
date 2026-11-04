"""가짜 AI — 인터넷·API Key·비용 없이 AI 응답을 흉내 낸다. (✅ 구현됨)

ai_client.call_ai_api(..., transport=FakeTransport()) 처럼 넘겨 쓰면
실제 HTTP 요청 대신 아래 함수가 불리고, 정해 둔 응답 JSON 을 돌려준다.

    fake = FakeTransport()
    text = call_ai_api('...', 'model', 0.3, 300,
                       api_key='test-key-not-real', transport=fake)
    fake.call_count        # 몇 번 불렸는지 (API 호출 횟수 확인)
    fake.calls[0]['body']  # 실제로 무엇을 보내려 했는지 확인

[중요] 이 가짜 AI 는 diff 를 "이해"하지 않습니다. 언제나 아래에 적힌
정해진 문장만 돌려줍니다. 실제 AI 결과는 Step 8 에서 1회만 확인하세요.
"""

import json

FAKE_COMMIT_TEXT = (
    'feat: 할 일 검색 기능 추가\n'
    '\n'
    '- todo_app/search.py 에 제목 키워드 검색 함수 추가\n'
    '- README 에 검색 사용 예시 추가'
)

FAKE_PR_TEXT = (
    'feat: 할 일 검색 기능 추가\n'
    '\n'
    '## Why\n'
    '- 할 일이 많아지면 원하는 항목을 찾기 어려워 검색 기능이 필요했습니다.\n'
    '\n'
    '## What\n'
    '- todo_app/search.py 에 키워드로 제목을 찾는 search_todos() 추가\n'
    '- README 에 검색 사용 예시 추가\n'
    '\n'
    '## How to Test\n'
    '- 할 일 2개를 추가한 뒤 search_todos("우유") 결과를 확인합니다.\n'
    '- python main.py pr 출력이 Why/What/How to Test 구조인지 확인합니다.'
)

# 길이 규칙(커밋 72자, PR 80자)을 일부러 어기는 응답 — Step 6, 7 연습용
FAKE_LONG_TITLE_TEXT = (
    'feat: ' + '아주 길게 늘어진 커밋 제목 예시 ' * 6 + '끝\n'
    '\n'
    '- todo_app/search.py 에 검색 함수 추가'
)

# 섹션이 빠진 PR 응답 — 형식 검증 연습용
FAKE_BROKEN_PR_TEXT = (
    'feat: 검색 기능 추가\n'
    '\n'
    '## Why\n'
    '- 검색이 필요했습니다.\n'
    '\n'
    '## What\n'
    '검색 함수를 추가했습니다. (불릿 없음)\n'
)


def make_anthropic_response(text, stop_reason='end_turn',
                            with_thinking=True):
    """Anthropic Messages API 응답 모양의 사전을 만든다.

    with_thinking=True 면 content 맨 앞에 thinking 블록을 넣는다.
    (최신 모델은 text 블록 앞에 thinking 블록을 돌려줄 수 있다.)
    """
    content = []
    if with_thinking:
        content.append({'type': 'thinking', 'thinking': '',
                        'signature': 'fake-signature'})
    content.append({'type': 'text', 'text': text})
    return {
        'id': 'msg_fake_0001',
        'type': 'message',
        'role': 'assistant',
        'model': 'fake-model',
        'content': content,
        'stop_reason': stop_reason,
        'usage': {'input_tokens': 321, 'output_tokens': 54},
    }


def make_openai_response(text, finish_reason='stop'):
    """OpenAI Chat Completions 응답 모양의 사전을 만든다."""
    return {
        'id': 'chatcmpl-fake-0001',
        'object': 'chat.completion',
        'model': 'fake-model',
        'choices': [{
            'index': 0,
            'message': {'role': 'assistant', 'content': text},
            'finish_reason': finish_reason,
        }],
        'usage': {'prompt_tokens': 321, 'completion_tokens': 54},
    }


class FakeTransport:
    """send_http_request 대신 쓰는 가짜 통신 함수(호출 가능한 객체).

    매개변수
        text  : 돌려줄 AI 글. None 이면 프롬프트에 'How to Test' 가 있으면
                FAKE_PR_TEXT, 없으면 FAKE_COMMIT_TEXT 를 돌려준다.
        error : 예외 객체. 주면 호출될 때 그 예외를 발생시킨다.
                (예: AIClientError('HTTP 401 ...') 로 인증 실패 흉내)
        texts : 여러 번 불릴 때 차례대로 돌려줄 글 목록 (재생성 연습용)
    """

    def __init__(self, text=None, error=None, texts=None):
        self.text = text
        self.error = error
        self.texts = list(texts) if texts else []
        self.calls = []

    @property
    def call_count(self):
        """지금까지 불린 횟수."""
        return len(self.calls)

    def __call__(self, url, headers, body, timeout):
        self.calls.append({
            'url': url,
            'headers': dict(headers),
            'body': body,
            'timeout': timeout,
        })
        if self.error is not None:
            raise self.error

        text = self._choose_text(body)
        if 'openai' in str(url):
            return make_openai_response(text)
        return make_anthropic_response(text)

    def _choose_text(self, body):
        index = len(self.calls) - 1
        if self.texts:
            return self.texts[min(index, len(self.texts) - 1)]
        if self.text is not None:
            return self.text
        if 'How to Test' in body_to_text(body):
            return FAKE_PR_TEXT
        return FAKE_COMMIT_TEXT

    def sent_text(self, index=-1):
        """index 번째 호출에서 보낸 본문 전체를 문자열로 돌려준다."""
        return body_to_text(self.calls[index]['body'])


def body_to_text(body):
    """요청 본문(사전/문자열/바이트)을 검색하기 쉬운 문자열로 바꾼다."""
    if isinstance(body, bytes):
        return body.decode('utf-8', errors='replace')
    if isinstance(body, str):
        return body
    return json.dumps(body, ensure_ascii=False)
