
"""AI 출력 형식 검증과 다듬기 (Step 6)."""

from ai_gitgen import config


def split_title_body(text):
    """AI 응답을 제목과 본문으로 나눈다."""
    lines = text.strip().splitlines()

    if lines and lines[0].strip().startswith('```'):
        lines = lines[1:]
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]

    if not lines:
        return '', ''

    title = lines[0].strip()
    body = '\n'.join(lines[1:]).strip()
    return title, body


def shorten_title(title, max_length):
    """제목이 길면 지정한 글자 수로 줄인다."""
    if len(title) <= max_length:
        return title
    return title[:max_length].rstrip()


def validate_commit_message(message, changed_paths=None):
    """커밋 메시지의 규칙 위반을 찾아 목록으로 반환한다."""
    problems = []
    title, body = split_title_body(message)

    if not title:
        problems.append('커밋 제목이 비어 있습니다.')
    elif len(title) > config.COMMIT_TITLE_MAX:
        problems.append(
            f'커밋 제목은 최대 {config.COMMIT_TITLE_MAX}자입니다.'
        )

    if body:
        has_bullet = any(
            line.strip().startswith(('- ', '* '))
            for line in body.splitlines()
        )
        has_file = any(
            path in body for path in (changed_paths or [])
        )

        if not has_bullet and not has_file:
            problems.append(
                '커밋 본문에는 불릿 또는 변경 파일 설명이 필요합니다.'
            )

    return problems


def validate_pr_title(title):
    """PR 제목의 길이와 줄 수를 확인한다."""
    problems = []

    if not title.strip():
        problems.append('PR 제목이 비어 있습니다.')
    if len(title.strip()) > config.PR_TITLE_MAX:
        problems.append(
            f'PR 제목은 최대 {config.PR_TITLE_MAX}자입니다.'
        )
    if len(title.splitlines()) > 1:
        problems.append('PR 제목은 한 줄이어야 합니다.')

    return problems


def validate_pr_body(body):
    """PR 본문의 필수 섹션과 불릿을 검사한다."""
    problems = []
    lines = body.splitlines()
    headers = {}

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('#'):
            continue

        heading = stripped.lstrip('#').strip()

        for section in config.PR_SECTIONS:
            if (heading == section
                    or heading.startswith(section + ' ')
                    or heading.startswith(section + '(')):
                headers.setdefault(section, index)

    for section in config.PR_SECTIONS:
        if section not in headers:
            problems.append(f'{section} 섹션이 없습니다.')
            continue

        start = headers[section] + 1
        end = len(lines)

        for index in range(start, len(lines)):
            if lines[index].strip().startswith('#'):
                end = index
                break

        has_bullet = any(
            line.strip().startswith(('- ', '* '))
            for line in lines[start:end]
        )

        if not has_bullet:
            problems.append(
                f'{section} 섹션에 불릿 항목이 없습니다.'
            )

    return problems


def format_commit_output(message):
    """커밋 메시지를 터미널 출력용으로 정리한다."""
    title, body = split_title_body(message)
    parts = ['--- Commit Message ---', title]

    if body:
        parts.extend(['', body])

    parts.append(config.SEPARATOR)
    return '\n'.join(parts)


def format_pr_output(title, body):
    """PR 제목과 본문을 터미널 출력용으로 정리한다."""
    return '\n'.join([
        '--- PR Title ---',
        title.strip(),
        '--- PR Body ---',
        body.strip(),
        config.SEPARATOR,
    ])
