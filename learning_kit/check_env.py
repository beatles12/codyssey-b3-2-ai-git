"""실습 환경 점검. (✅ 구현됨)

사용법
    python -m learning_kit.check_env

확인하는 것
    1. Python 버전이 3.10 이상인가
    2. git 명령을 쓸 수 있는가
    3. 프로젝트 폴더에서 실행했는가
    4. AI_API_KEY 환경변수가 있는가 (값은 절대 출력하지 않음)
    5. 기본 환경 테스트(tests/base)가 모두 통과하는가
"""

import os
import platform
import shutil
import subprocess
import sys

from learning_kit.paths import PROJECT_ROOT


def _line(ok, text):
    mark = '[OK]  ' if ok else '[확인]'
    print(f'  {mark} {text}')
    return ok


def main():
    print('=' * 70)
    print(' B3-2 실습 환경 점검')
    print('=' * 70)
    all_ok = True

    version = sys.version_info
    all_ok &= _line(version >= (3, 10),
                    f'Python {platform.python_version()} '
                    '(3.10 이상 필요)')

    git_path = shutil.which('git')
    if git_path:
        result = subprocess.run(['git', '--version'], capture_output=True,
                                text=True)
        all_ok &= _line(result.returncode == 0, result.stdout.strip())
    else:
        all_ok &= _line(False, 'git 을 찾을 수 없습니다. Git 을 설치하세요.')

    in_root = os.path.abspath(os.getcwd()) == str(PROJECT_ROOT)
    _line(in_root, f'현재 폴더: {os.getcwd()}')
    if not in_root:
        print(f'         프로젝트 폴더로 이동하세요: cd {PROJECT_ROOT}')

    has_key = bool(os.environ.get('AI_API_KEY', '').strip())
    if has_key:
        _line(True, 'AI_API_KEY 설정됨 (값은 보안상 표시하지 않습니다)')
    else:
        print('  [안내] AI_API_KEY 없음 — Step 1~7 은 키 없이 연습합니다. '
              'Step 8 에서만 필요합니다.')

    print()
    from learning_kit.practice import run_base
    base_ok = run_base()
    all_ok &= base_ok

    if all_ok:
        print('다음 할 일: START_HERE.md 의 "학습 순서"를 따라 Step 1 을 '
              '시작하세요.')
        print('           python -m learning_kit.practice     (진행 현황표)')
        return 0
    print('위의 [확인] 항목을 먼저 해결하세요. START_HERE.md 의 '
          '"문제가 생겼을 때"를 참고하세요.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
