"""안전 모드 --safe-mode (🧩 Step 3). 명세: docs/modules/safety.md"""

import re  # noqa: F401  (Step 3 에서 사용합니다)

from ai_gitgen import config  # noqa: F401  (Step 3 에서 사용합니다)

# ✅ 구현됨 — 가려진 자리에 넣을 글자
MASK_TEXT = '[MASKED]'

# 🧩 Step 3 — (이름, 정규식) 목록. 필수: sk- 키·이메일, 선택: 대입값·전화번호
SENSITIVE_PATTERNS = [
    # TODO(Step 3): 예) ('이름', r'정규표현식'),
]


def mask_sensitive(text):
    """text 안의 민감정보를 MASK_TEXT 로 바꾼 새 문자열을 돌려준다."""
    # TODO(Step 3): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 3 - safety.mask_sensitive()')


def limit_diff(diff_text, max_files=config.SAFE_MODE_MAX_FILES,
               max_lines=config.SAFE_MODE_MAX_LINES):
    """[선택] diff 를 최대 max_files 개 파일, max_lines 줄로 자른다."""
    # TODO(Step 3): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 3 - safety.limit_diff()')


def apply_safe_mode(diff_text, enabled=True):
    """enabled 면 마스킹(필수)·전송 제한(선택)을 적용하고, 아니면 그대로 둔다."""
    # TODO(Step 3): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 3 - safety.apply_safe_mode()')
