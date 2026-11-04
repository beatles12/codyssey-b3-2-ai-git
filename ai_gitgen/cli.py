"""명령줄 처리와 전체 흐름 연결 (🧩 Step 1, 7). 명세: docs/modules/cli.md"""

import argparse  # noqa: F401  (Step 1 에서 사용합니다)
import sys

from ai_gitgen import config  # noqa: F401  (Step 1, Step 7 에서 사용합니다)


# ✅ 구현됨 — 출력 형식 예시
def log(level, message):
    """머리표([INFO] 등)를 붙여 한 줄 출력한다. [ERROR] 만 표준 오류로 보낸다."""
    stream = sys.stderr if level == 'ERROR' else sys.stdout
    print(f'[{level}] {message}', file=stream)


# 🧩 Step 1 — 명령줄 옵션 만들기
def build_parser():
    """commit / pr 하위 명령과 공통 옵션을 가진 ArgumentParser 를 만든다."""
    # TODO(Step 1): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 1 - cli.build_parser()')


def validate_options(args):
    """옵션 값이 허용 범위인지 검사해 문제 메시지 list 를 돌려준다."""
    # TODO(Step 1): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 1 - cli.validate_options()')


# 🧩 Step 7 — 전체 흐름 연결
def run_commit(args, cwd=None, transport=None):
    """commit 흐름을 실행하고 종료 코드를 돌려준다."""
    # TODO(Step 7): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 7 - cli.run_commit()')


def run_pr(args, cwd=None, transport=None):
    """pr 흐름을 실행하고 종료 코드를 돌려준다."""
    # TODO(Step 7): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 7 - cli.run_pr()')


def main(argv=None, cwd=None, transport=None):
    """옵션을 해석·검사한 뒤 commit / pr 흐름으로 보내고 종료 코드를 돌려준다."""
    # TODO(Step 7): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 7 - cli.main()')
