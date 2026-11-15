
"""AI에게 보낼 프롬프트 구성 (Step 4). 명세: docs/modules/prompt_builder.md"""

from ai_gitgen import config


def format_file_list(changed_files):
    """변경된 파일 목록을 읽기 좋은 문자열로 만든다."""
    if not changed_files:
        return '변경된 파일이 없습니다.'

    return '\n'.join(
        f"- [{item['code']}] {item['path']}"
        for item in changed_files
    )


def build_commit_prompt(changed_files, diff_text):
    """AI에게 커밋 메시지 작성을 요청하는 지시서를 만든다."""
    return (
        '당신은 Git 변경사항을 설명하는 개발 도우미입니다.\n'
        '아래 자료를 근거로 한국어 커밋 메시지를 작성하세요.\n'
        f'제목은 {config.COMMIT_TITLE_RECOMMENDED}자 이내를 권장하며 '
        f'최대 {config.COMMIT_TITLE_MAX}자를 넘지 마세요.\n'
        '제목은 한 줄로 작성하고, 필요한 경우 핵심 변경을 불릿으로 요약하세요.\n'
        '자료에 없는 변경 내용은 추측하지 마세요.\n\n'
        f'변경된 파일:\n{format_file_list(changed_files)}\n\n'
        f'Git diff:\n{diff_text}'
    )


def build_pr_prompt(changed_files, diff_text, branch_name):
    """AI에게 PR 제목과 본문 작성을 요청하는 지시서를 만든다."""
    return (
        '당신은 GitHub PR 초안을 작성하는 개발 도우미입니다.\n'
        '아래 자료를 근거로 한국어 PR 제목과 본문을 작성하세요.\n'
        f'PR 제목은 최대 {config.PR_TITLE_MAX}자를 넘지 마세요.\n'
        '본문에는 다음 세 가지 제목을 반드시 포함하세요.\n'
        '## Why\n'
        '## What\n'
        '## How to Test\n'
        '각 항목에 최소 한 개 이상의 구체적인 불릿을 작성하세요.\n'
        '실제로 확인하지 않은 테스트는 통과했다고 쓰지 마세요.\n'
        '자료에 없는 변경 내용은 추측하지 마세요.\n\n'
        f'현재 브랜치: {branch_name}\n'
        f'변경된 파일:\n{format_file_list(changed_files)}\n\n'
        f'Git diff:\n{diff_text}'
    )