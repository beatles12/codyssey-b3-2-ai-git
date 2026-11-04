"""B3-2 AI 커밋/PR 초안 생성기 실행 파일. 사용법: python main.py commit | pr"""

import functools
import sys

from ai_gitgen.cli import main


def show_todo_hint(func):
    """[학습 지원] TODO 함수가 불리면 Traceback 대신 남은 단계를 안내한다."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotImplementedError as error:
            print(f'[TODO] 아직 구현하지 않은 기능입니다: {error}')
            print('[TODO] START_HERE.md 와 docs/PRACTICE_STEPS.md 를 참고하세요.')
            return 3
    return wrapper


@show_todo_hint
def run():
    """프로그램을 실행하고 종료 코드(0=정상)를 돌려준다."""
    return main()


if __name__ == '__main__':
    sys.exit(run())
