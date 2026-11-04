"""출력 형식 검증과 다듬기 (🧩 Step 6). 명세: docs/modules/formatter.md"""

from ai_gitgen import config  # noqa: F401  (Step 6 에서 사용합니다)


def split_title_body(text):
    """AI 응답 글을 (제목, 본문) 으로 나눈다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.split_title_body()')


def shorten_title(title, max_length):
    """제목이 max_length 글자보다 길면 그 이하로 줄인다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.shorten_title()')


def validate_commit_message(message, changed_paths=None):
    """커밋 메시지 규칙 위반을 문제 메시지 list 로 돌려준다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.validate_commit_message()')


def validate_pr_title(title):
    """PR 제목 문제(빈 제목, 80자 초과, 여러 줄)를 list 로 돌려준다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.validate_pr_title()')


def validate_pr_body(body):
    """PR 본문 섹션·불릿 규칙 위반을 문제 메시지 list 로 돌려준다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.validate_pr_body()')


def format_commit_output(message):
    """커밋 메시지를 구획이 나뉜 터미널 출력 문자열로 만든다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.format_commit_output()')


def format_pr_output(title, body):
    """PR 제목·본문을 구획이 나뉜 터미널 출력 문자열로 만든다."""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.format_pr_output()')
