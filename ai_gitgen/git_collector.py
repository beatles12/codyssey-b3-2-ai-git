"""Git 변경 사항 수집 (🧩 Step 2). 명세: docs/modules/git_collector.md"""

import subprocess  # noqa: F401  (Step 2 에서 사용합니다)


# ✅ 구현됨 — 이 모듈 전용 예외(오류) 종류
class GitCommandError(Exception):
    """git 명령이 실패했을 때 쓰는 예외."""


# 🧩 Step 2
def run_git(args, cwd=None):
    """git 명령을 실행하고 표준 출력 문자열을 돌려준다. 실패하면 GitCommandError."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.run_git()')


def is_git_repository(cwd=None):
    """cwd 가 Git 저장소 안이면 True, 아니면 False 를 돌려준다."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.is_git_repository()')


def parse_status_output(status_text):
    """git status --porcelain 출력을 파일 목록 [{code, path}] 으로 바꾼다."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.parse_status_output()')


def get_changed_files(cwd=None):
    """변경된 파일 목록을 돌려준다. 변경이 없으면 []."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.get_changed_files()')


def get_diff(cwd=None):
    """staged 와 unstaged 변경을 모두 담은 diff 텍스트를 돌려준다."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.get_diff()')


def count_diff_lines(diff_text):
    """diff 텍스트의 줄 수를 센다."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.count_diff_lines()')


def get_current_branch(cwd=None):
    """현재 브랜치 이름을 돌려준다."""
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.get_current_branch()')
