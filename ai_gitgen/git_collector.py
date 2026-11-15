
"""Git 변경 사항 수집 (Step 2). 명세: docs/modules/git_collector.md"""

import subprocess


class GitCommandError(Exception):
    """Git 명령 실행 실패를 나타낸다."""


def run_git(args, cwd=None):
    """Git 명령을 실행하고 출력된 문자열을 반환한다."""
    try:
        result = subprocess.run(
            ['git', '-c', 'core.quotepath=false', *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
    except OSError as error:
        raise GitCommandError(f'Git을 실행할 수 없습니다: {error}') from error

    if result.returncode != 0:
        message = result.stderr.strip() or '알 수 없는 Git 오류'
        raise GitCommandError(f'Git 명령 실행 실패: {message}')

    return result.stdout


def is_git_repository(cwd=None):
    """현재 폴더가 Git 저장소에 속하는지 확인한다."""
    try:
        run_git(['status', '--porcelain'], cwd)
        return True
    except GitCommandError:
        return False


def parse_status_output(status_text):
    """Git 상태 출력을 변경 파일 목록으로 변환한다."""
    files = []

    for line in status_text.splitlines():
        if not line.strip():
            continue

        code = line[:2].strip()
        path = line[3:].strip()

        if ' -> ' in path:
            path = path.rsplit(' -> ', 1)[-1]

        files.append({'code': code, 'path': path})

    return files


def get_changed_files(cwd=None):
    """변경된 파일 목록을 반환한다."""
    output = run_git(['status', '--porcelain'], cwd)
    return parse_status_output(output)


def get_diff(cwd=None):
    """커밋 준비 전후의 변경 내용을 모두 수집한다."""
    staged = run_git(['diff', '--cached'], cwd)
    unstaged = run_git(['diff'], cwd)
    return '\n'.join(part for part in (staged, unstaged) if part)


def count_diff_lines(diff_text):
    """Git diff 텍스트의 줄 수를 반환한다."""
    return len(diff_text.splitlines())


def get_current_branch(cwd=None):
    """Git 상태 정보에서 현재 브랜치 이름을 가져온다."""
    output = run_git(['status', '--porcelain', '--branch'], cwd)
    first_line = output.splitlines()[0]
    return first_line[3:].split('...')[0].strip()
