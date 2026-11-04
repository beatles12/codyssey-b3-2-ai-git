"""안전 모드(--safe-mode) — AI 에게 보내기 전에 diff 를 안전하게 만든다.

[실습 단계] 🧩 Step 3

[공식 제약사항]
    git diff 에 들어 있을 수 있는 민감정보(API Key, 개인정보 등)는
    프롬프트에 포함하지 않도록 주의한다. 아래 중 1개 이상을 제공한다.
        (A) 특정 패턴(API Key 형태, 이메일 등)을 마스킹한 뒤 전송
        (B) diff 일부만 전송 (예: 최대 10개 파일, 최대 200줄)
    이 실습에서는 (A)와 (B)를 모두 연습한다.

[자주 쓰는 표준 라이브러리]
    re : 정규표현식(문자열 패턴 찾기/바꾸기)
"""

import re  # noqa: F401  (Step 3 에서 사용합니다)

from ai_gitgen import config  # noqa: F401  (Step 3 에서 사용합니다)

# ✅ 구현됨 — 가려진 자리에 넣을 글자
MASK_TEXT = '[MASKED]'

# 🧩 Step 3 — 가릴 패턴 목록을 직접 채우세요.
#   형식: (이름, 정규표현식 문자열) 튜플의 리스트
#   최소한 다음 세 가지를 가려야 테스트를 통과합니다.
#     1) 'sk-' 로 시작하는 긴 API Key 모양 문자열
#     2) api_key / secret / token / password 같은 이름 뒤에 = 또는 : 로
#        이어지는 값  (예: API_KEY = "...", DB_PASSWORD = "...",
#        secret: '...')  — 대문자/소문자 모두
#     3) 이메일 주소
#   선택: 휴대전화 번호(010-1234-5678 형태)
SENSITIVE_PATTERNS = [
    # TODO(Step 3): 예) ('이름', r'정규표현식'),
]


def mask_sensitive(text):
    """text 안의 민감정보를 MASK_TEXT 로 바꾼 새 문자열을 돌려준다.

    - 민감정보가 아닌 부분은 한 글자도 바뀌면 안 된다.
    - 예) 'API_KEY = "fake-key-123456"'  ->  'API_KEY = "[MASKED]"'
          'contact: kim@example.com'  ->  'contact: [MASKED]'

    힌트: SENSITIVE_PATTERNS 를 돌면서 re.sub() 를 적용한다.
    """
    # TODO(Step 3): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 3 - safety.mask_sensitive()')


def limit_diff(diff_text, max_files=config.SAFE_MODE_MAX_FILES,
               max_lines=config.SAFE_MODE_MAX_LINES):
    """diff 를 앞에서부터 최대 max_files 개 파일, 최대 max_lines 줄로 자른다.

    규칙
        - 파일 하나의 diff 는 'diff --git ' 으로 시작하는 줄부터 시작한다.
        - 파일 수 제한을 먼저 적용하고, 그다음 전체 줄 수를 제한한다.
        - 잘라 낸 내용이 있으면 맨 끝에 안내 줄 1개를 덧붙인다.
          예) '... (safe-mode: 120줄 생략)'
        - 제한보다 작으면 원래 문자열을 그대로 돌려준다.

    왜 필요할까?
        diff 가 길수록 AI 요청 비용(토큰)이 커지고, 민감한 파일이 섞일
        가능성도 커진다. 보내는 양에 상한을 두면 둘 다 줄일 수 있다.
    """
    # TODO(Step 3): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 3 - safety.limit_diff()')


def apply_safe_mode(diff_text, enabled=True):
    """enabled 가 True 면 마스킹과 전송 제한을 적용하고, False 면 그대로 둔다.

    반환값
        str : AI 에게 보낼 diff 텍스트
    """
    # TODO(Step 3): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 3 - safety.apply_safe_mode()')
