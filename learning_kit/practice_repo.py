"""연습용 Git 저장소 만들기. (✅ 구현됨)

사용법
    python -m learning_kit.practice_repo            # 기본: feature 시나리오
    python -m learning_kit.practice_repo secret     # 시나리오 고르기
    python -m learning_kit.practice_repo --list     # 시나리오 목록 보기

만들어지는 곳: 프로젝트 안의 practice_repo/ 폴더 (.gitignore 에 등록됨)
    - 프로젝트 저장소와는 완전히 별개인 작은 Git 저장소입니다.
    - 다시 실행하면 기존 연습 저장소를 지우고 새로 만듭니다.
      (이 스크립트가 만든 폴더만 지웁니다. 다른 폴더는 절대 지우지 않습니다.)

만든 뒤에는
    cd practice_repo
    git status
    python ../main.py commit        # Step 7 이후
"""

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from learning_kit.paths import PRACTICE_REPO_DIR

# .git 폴더 안에 두는 표시 파일. 이 파일이 있는 폴더만 지운다.
MARKER_NAME = 'b3-2-practice-repo'

PRACTICE_USER_NAME = 'Practice Learner'
PRACTICE_USER_EMAIL = 'learner@example.com'

SCENARIOS = {
    'feature': ('feature/add-search',
                '검색 기능 추가 — staged 2개 + unstaged 1개 (기본 실습용)'),
    'bugfix': ('fix/empty-title',
               '빈 제목 버그 수정 — 작은 unstaged 변경 1개'),
    'clean': ('main',
              '변경 없음 — "변경 사항이 없습니다" 확인용'),
    'staged-only': ('feature/add-search',
                    'git add 한 변경만 있음 — git diff --cached 확인용'),
    'unstaged-only': ('feature/add-search',
                      'git add 안 한 변경만 있음 — git diff 확인용'),
    'untracked-only': ('docs/add-notes',
                       '새 파일(추적 안 됨)만 있음 — status 와 diff 차이 확인'),
    'secret': ('feature/api-settings',
               '가짜 API Key·이메일·전화번호가 들어간 변경 — safe-mode 연습'),
    'large': ('refactor/split-modules',
              '파일 15개·300줄 이상 변경 — 전송 제한(10파일/200줄) 연습'),
}

# ---------------------------------------------------------------------------
# 처음 커밋에 들어갈 작은 "할 일 관리" 프로그램
# ---------------------------------------------------------------------------
BASE_FILES = {
    'README.md': (
        '# Todo App (연습용)\n'
        '\n'
        '할 일을 추가하고 목록을 보는 아주 작은 프로그램입니다.\n'
        '\n'
        '## 사용 예\n'
        '\n'
        '- add_todo("우유 사기")\n'
        '- list_todos()\n'
    ),
    'todo_app/__init__.py': '"""할 일 관리 패키지 (연습용)."""\n',
    'todo_app/app.py': (
        '"""간단한 할 일 관리 프로그램 (연습용)."""\n'
        '\n'
        'TODOS = []\n'
        '\n'
        '\n'
        'def add_todo(title):\n'
        '    """할 일을 추가하고 전체 개수를 돌려준다."""\n'
        "    TODOS.append({'title': title, 'done': False})\n"
        '    return len(TODOS)\n'
        '\n'
        '\n'
        'def list_todos():\n'
        '    """할 일 목록을 돌려준다."""\n'
        '    return list(TODOS)\n'
    ),
    'todo_app/settings.py': (
        '"""앱 설정 (연습용)."""\n'
        '\n'
        "APP_NAME = 'Todo App'\n"
        'DEBUG = False\n'
    ),
}

SEARCH_FILE = (
    '"""할 일 검색 기능."""\n'
    '\n'
    'from todo_app.app import list_todos\n'
    '\n'
    '\n'
    'def search_todos(keyword):\n'
    '    """제목에 keyword 가 들어간 할 일만 돌려준다."""\n'
    '    keyword = keyword.strip().lower()\n'
    "    return [todo for todo in list_todos()\n"
    "            if keyword in todo['title'].lower()]\n"
)

APP_WITH_COMPLETE = BASE_FILES['todo_app/app.py'].replace(
    "    TODOS.append({'title': title, 'done': False})\n",
    "    TODOS.append({'title': title.strip(), 'done': False})\n",
) + (
    '\n'
    '\n'
    'def complete_todo(index):\n'
    '    """index 번째 할 일을 완료로 표시한다."""\n'
    "    TODOS[index]['done'] = True\n"
)

APP_WITH_BUGFIX = BASE_FILES['todo_app/app.py'].replace(
    '    """할 일을 추가하고 전체 개수를 돌려준다."""\n',
    '    """할 일을 추가하고 전체 개수를 돌려준다."""\n'
    '    if not title.strip():\n'
    "        raise ValueError('할 일 제목이 비어 있습니다.')\n",
)

# safe-mode 연습용 "가짜" 민감정보. 실제 키가 아닙니다.
SETTINGS_WITH_SECRETS = BASE_FILES['todo_app/settings.py'] + (
    '\n'
    '# 외부 서비스 연동 설정 (연습용 가짜 값)\n'
    'API_KEY = "sk-fake-practice-0000000000abcdef"\n'
    'ADMIN_EMAIL = "admin@example.com"\n'
    'SUPPORT_PHONE = "010-1234-5678"\n'
    'DB_PASSWORD = "fake-password-1234"\n'
)

NOTES_FILE = (
    '# 개발 메모\n'
    '\n'
    '- 다음에는 마감일(due date) 기능을 추가하자.\n'
)


def _make_module_file(number):
    """large 시나리오용 25줄짜리 모듈 파일 내용을 만든다."""
    lines = [f'"""분리된 모듈 {number:02d} (연습용)."""', '']
    for index in range(1, 12):
        lines.append(f'def helper_{number:02d}_{index:02d}():')
        lines.append(f'    return {number * 100 + index}')
    lines.append('')
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# 내부 도우미 함수
# ---------------------------------------------------------------------------
def _git(repo, *args):
    """연습 저장소 안에서 git 명령을 실행한다. 실패하면 예외를 던진다."""
    command = [
        'git',
        '-c', f'user.name={PRACTICE_USER_NAME}',
        '-c', f'user.email={PRACTICE_USER_EMAIL}',
        '-c', 'commit.gpgsign=false',
        '-c', 'core.autocrlf=false',
        '-c', 'init.defaultBranch=main',
        *args,
    ]
    result = subprocess.run(
        command, cwd=repo, capture_output=True, text=True,
        encoding='utf-8', errors='replace',
    )
    if result.returncode != 0:
        raise RuntimeError(
            f'git {" ".join(args)} 실패: {result.stderr.strip()}'
        )
    return result.stdout


def _write(repo, relative_path, content):
    """연습 저장소 안에 파일을 쓴다. (줄바꿈은 항상 \\n)"""
    path = Path(repo) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        file.write(content)


def _on_remove_error(function, path, _excinfo):
    """Windows 에서 읽기 전용 .git 파일 삭제가 실패할 때 권한을 풀고 재시도."""
    os.chmod(path, stat.S_IWRITE)
    function(path)


def remove_practice_repo(target):
    """이 스크립트가 만든 연습 저장소만 지운다. 다른 폴더면 오류."""
    target = Path(target)
    if not target.exists():
        return
    if not target.is_dir():
        raise RuntimeError(f'{target} 은(는) 폴더가 아니라서 지우지 않습니다.')
    if (target / '.git' / MARKER_NAME).exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(target, onexc=_on_remove_error)
        else:
            shutil.rmtree(target, onerror=_on_remove_error)
        return
    if any(target.iterdir()):
        raise RuntimeError(
            f'{target} 에 다른 파일이 있어 지우지 않습니다. '
            '연습 저장소가 아닌 폴더는 직접 확인한 뒤 정리하세요.'
        )


# ---------------------------------------------------------------------------
# 시나리오별 변경 만들기
# ---------------------------------------------------------------------------
def _apply_scenario(repo, scenario):
    branch, _description = SCENARIOS[scenario]
    if branch != 'main':
        _git(repo, 'checkout', '-q', '-b', branch)

    if scenario == 'feature':
        _write(repo, 'todo_app/search.py', SEARCH_FILE)
        _write(repo, 'README.md',
               BASE_FILES['README.md'] + '- search_todos("우유")\n')
        _git(repo, 'add', 'todo_app/search.py', 'README.md')
        _write(repo, 'todo_app/app.py', APP_WITH_COMPLETE)   # unstaged
    elif scenario == 'bugfix':
        _write(repo, 'todo_app/app.py', APP_WITH_BUGFIX)
    elif scenario == 'staged-only':
        _write(repo, 'todo_app/search.py', SEARCH_FILE)
        _git(repo, 'add', 'todo_app/search.py')
    elif scenario == 'unstaged-only':
        _write(repo, 'todo_app/app.py', APP_WITH_COMPLETE)
    elif scenario == 'untracked-only':
        _write(repo, 'NOTES.md', NOTES_FILE)
    elif scenario == 'secret':
        _write(repo, 'todo_app/settings.py', SETTINGS_WITH_SECRETS)
    elif scenario == 'large':
        for number in range(1, 16):
            _write(repo, f'todo_app/modules/module_{number:02d}.py',
                   _make_module_file(number))
        _git(repo, 'add', 'todo_app/modules')
    # 'clean' 은 아무것도 바꾸지 않는다.


def create_practice_repo(target=PRACTICE_REPO_DIR, scenario='feature'):
    """연습용 Git 저장소를 새로 만들고 그 경로(Path)를 돌려준다."""
    if scenario not in SCENARIOS:
        names = ', '.join(SCENARIOS)
        raise ValueError(f'모르는 시나리오: {scenario} (가능: {names})')

    target = Path(target)
    remove_practice_repo(target)
    target.mkdir(parents=True, exist_ok=True)

    _git(target, 'init', '-q')
    (target / '.git' / MARKER_NAME).write_text(
        'B3-2 연습용 저장소 표시 파일\n', encoding='utf-8')
    # 학습자가 이 폴더에서 직접 git commit 을 해 볼 수 있도록
    # "이 저장소에만" 이름/이메일을 설정한다. (전역 설정은 건드리지 않음)
    _git(target, 'config', 'user.name', PRACTICE_USER_NAME)
    _git(target, 'config', 'user.email', PRACTICE_USER_EMAIL)
    _git(target, 'config', 'commit.gpgsign', 'false')

    for relative_path, content in BASE_FILES.items():
        _write(target, relative_path, content)
    _git(target, 'add', '.')
    _git(target, 'commit', '-q', '-m', 'chore: 할 일 관리 앱 초기 버전')

    _apply_scenario(target, scenario)
    return target


# ---------------------------------------------------------------------------
# 명령줄 실행
# ---------------------------------------------------------------------------
def _print_scenarios():
    print('사용 가능한 시나리오')
    for name, (branch, description) in SCENARIOS.items():
        print(f'  {name:<15} 브랜치 {branch:<24} {description}')


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='python -m learning_kit.practice_repo',
        description='연습용 Git 저장소를 만듭니다.')
    parser.add_argument('scenario', nargs='?', default='feature',
                        help='시나리오 이름 (기본: feature)')
    parser.add_argument('--path', default=str(PRACTICE_REPO_DIR),
                        help='만들 위치 (기본: 프로젝트/practice_repo)')
    parser.add_argument('--list', action='store_true',
                        help='시나리오 목록만 보여 주기')
    args = parser.parse_args(argv)

    if args.list:
        _print_scenarios()
        return 0
    try:
        repo = create_practice_repo(args.path, args.scenario)
    except (ValueError, RuntimeError) as error:
        print(f'[ERROR] {error}', file=sys.stderr)
        _print_scenarios()
        return 1

    branch, description = SCENARIOS[args.scenario]
    status = _git(repo, 'status', '--short') or '(변경 없음)\n'
    print(f'[DONE] 연습 저장소를 만들었습니다: {repo}')
    print(f'[INFO] 시나리오: {args.scenario} — {description}')
    print(f'[INFO] 현재 브랜치: {branch}')
    print('[INFO] git status --short 결과')
    print(status, end='')
    print()
    print('다음에 해 볼 것')
    print(f'  cd {repo}')
    print('  git status            # 바뀐 파일 목록')
    print('  git diff              # git add 안 한 변경')
    print('  git diff --cached     # git add 한 변경')
    print('  git log --oneline     # 커밋 기록')
    return 0


if __name__ == '__main__':
    sys.exit(main())
