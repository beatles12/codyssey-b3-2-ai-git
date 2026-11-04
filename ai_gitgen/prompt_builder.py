"""AI 에게 보낼 프롬프트 구성 (🧩 Step 4). 명세: docs/modules/prompt_builder.md"""

from ai_gitgen import config  # noqa: F401  (Step 4 에서 사용합니다)


def format_file_list(changed_files):
    """변경 파일 목록을 사람이 읽기 좋은 여러 줄 문자열로 바꾼다."""
    # TODO(Step 4): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 4 - prompt_builder.format_file_list()')


def build_commit_prompt(changed_files, diff_text):
    """커밋 메시지 생성을 부탁하는 프롬프트 문자열을 만든다."""
    # TODO(Step 4): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 4 - prompt_builder.build_commit_prompt()')


def build_pr_prompt(changed_files, diff_text, branch_name):
    """PR 제목·본문 초안 생성을 부탁하는 프롬프트 문자열을 만든다."""
    # TODO(Step 4): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 4 - prompt_builder.build_pr_prompt()')
