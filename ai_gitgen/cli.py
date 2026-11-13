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
    """전체 명령어 해석기 (식당 주문 시스템)"""
    parser = argparse.ArgumentParser(description='AI 커밋/ PR 초안 생성기')

    """commit, pr 같은 하위 명령어 등록 도구 (메뉴 종류를 관리하는 메뉴판)"""
    commands = parser.add_subparsers(dest='command', required=True)

    for name in ('commit', 'pr'):
        command = commands.add_parser(name)
        command.add_argument('--model', default=config.DEFAULT_MODEL)
        command.add_argument('--temperature', type=float, default=config.DEFAULT_TEMPERATURE)
        command.add_argument('--max-tokens', type=int, default=config.DEFAULT_MAX_TOKENS)
        command.add_argument('--safe-mode', action='store_true')

    return parser

def validate_options(args):
    """사용자가 입력한 옵션을 검사하고 문제 메시지 목록을 반환한다."""
    problems = []

    if not args.model.strip():
        problems.append('model: 모델 이름을 입력하세요.')

    if not config.TEMPERATURE_MIN <= args.temperature <= config.TEMPERATURE_MAX:
        problems.append('temperature: 허용 범위는 0.0~1.0입니다.')

    if not config.MAX_TOKENS_MIN <= args.max_tokens <= config.MAX_TOKENS_LIMIT:
        problems.append('max_tokens: 허용 범위는 1~4096입니다.')

    return problems



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
