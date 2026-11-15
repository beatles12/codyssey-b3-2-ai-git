
"""안전 모드 --safe-mode (Step 3). 명세: docs/modules/safety.md"""

import re

from ai_gitgen import config

MASK_TEXT = '[MASKED]'

SENSITIVE_PATTERNS = [
    ('API 키', r'sk-[A-Za-z0-9_-]{16,}'),
    ('이메일', r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
]


def mask_sensitive(text):
    """민감정보를 찾아 [MASKED]로 바꾼다."""
    masked_text = text

    for name, pattern in SENSITIVE_PATTERNS:
        masked_text = re.sub(pattern, MASK_TEXT, masked_text)

    return masked_text


def limit_diff(diff_text, max_files=config.SAFE_MODE_MAX_FILES,
               max_lines=config.SAFE_MODE_MAX_LINES):
    """[선택] 전송할 diff의 파일 수와 줄 수를 제한한다."""
    raise NotImplementedError('Step 3 - safety.limit_diff()')


def apply_safe_mode(diff_text, enabled=True):
    """안전 모드가 켜져 있으면 민감정보를 가린다."""
    if not enabled:
        return diff_text

    return mask_sensitive(diff_text)
