"""B3-2 AI 커밋/PR 초안 생성기 — 실행 파일(진입점).

사용 예 (Step 7 까지 구현한 뒤)
    python main.py commit
    python main.py pr
    python main.py commit --temperature 0.2 --max-tokens 300 --safe-mode

[상태] ✅ 구현됨
    이 파일은 ai_gitgen.cli.main() 을 부르기만 합니다.
    실제 기능은 ai_gitgen 패키지 안의 TODO 함수들을 구현해야 동작합니다.
"""

import sys

from ai_gitgen.cli import main


def run():
    """프로그램을 실행하고 종료 코드(0=정상)를 돌려준다.

    [학습 지원] 아직 구현하지 않은 TODO 함수가 호출되면
    긴 오류 화면(Traceback) 대신 어떤 단계가 남았는지 알려 준다.
    """
    try:
        return main()
    except NotImplementedError as error:
        print(f'[TODO] 아직 구현하지 않은 기능입니다: {error}')
        print('[TODO] START_HERE.md 와 docs/PRACTICE_STEPS.md 를 참고하세요.')
        return 3


if __name__ == '__main__':
    sys.exit(run())
