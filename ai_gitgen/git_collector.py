"""Git 변경 사항 수집 — git status / git diff 결과를 프로그램 입력으로 바꾼다.

[실습 단계] 🧩 Step 2

[이 파일이 하는 일]
    Python 에서 git 명령을 실행하고, 그 출력(문자열)을 정리해서
    "어떤 파일이 바뀌었는지"와 "무엇이 바뀌었는지(diff)"를 돌려준다.

[왜 AI 호출 코드와 분리할까?]  (공식 체크리스트 항목 2)
    - Git 수집은 내 컴퓨터 안에서 끝나는 일, AI 호출은 인터넷 너머의 일이다.
    - 둘을 나누면 AI 없이도 Git 부분만 테스트할 수 있고,
      AI 제공자를 바꿔도 이 파일은 고칠 필요가 없다.

[자주 쓰는 표준 라이브러리]
    subprocess : 외부 프로그램(git) 실행
"""

import subprocess  # noqa: F401  (Step 2 에서 사용합니다)


# ---------------------------------------------------------------------------
# ✅ 구현됨 — 이 모듈 전용 예외(오류) 종류
# ---------------------------------------------------------------------------
class GitCommandError(Exception):
    """git 명령이 실패했을 때(종료 코드가 0 이 아닐 때) 사용하는 예외."""


# ---------------------------------------------------------------------------
# 🧩 Step 2
# ---------------------------------------------------------------------------
def run_git(args, cwd=None):
    """git 명령을 실행하고 표준 출력(stdout) 문자열을 돌려준다.

    매개변수
        args : git 뒤에 붙일 인자 목록. 예) ['status', '--porcelain']
        cwd  : 명령을 실행할 폴더 (None 이면 현재 폴더)

    반환값
        str : git 이 출력한 내용

    오류
        - git 이 0 이 아닌 종료 코드로 끝나면 GitCommandError 를 발생시킨다.
          (오류 메시지에 git 의 stderr 내용을 담아 두면 원인 찾기가 쉽다.)
        - git 프로그램 자체가 없으면(FileNotFoundError) 이것도
          GitCommandError 로 바꿔서 발생시킨다.

    구현 힌트는 교재 Step 2 를 보세요. (subprocess.run, capture_output,
    text, encoding='utf-8', returncode)
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.run_git()')


def is_git_repository(cwd=None):
    """cwd 가 Git 저장소(작업 폴더) 안이면 True, 아니면 False.

    힌트: `git rev-parse --is-inside-work-tree` 는 저장소 안에서
    'true' 를 출력하고, 저장소 밖에서는 실패(오류)한다.
    이 함수는 예외를 밖으로 내보내지 말고 True / False 만 돌려준다.
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.is_git_repository()')


def parse_status_output(status_text):
    """`git status --porcelain` 출력 문자열을 파일 목록으로 바꾼다.

    입력 예 (각 줄의 앞 2글자가 상태 코드, 3번째 글자는 공백)
        ' M todo_app/app.py'
        'A  todo_app/search.py'
        '?? notes.txt'
        'R  docs/old.md -> docs/new.md'

    반환값 예
        [
            {'code': 'M', 'path': 'todo_app/app.py'},
            {'code': 'A', 'path': 'todo_app/search.py'},
            {'code': '??', 'path': 'notes.txt'},
            {'code': 'R', 'path': 'docs/new.md'},
        ]

    규칙
        - code : 앞 2글자에서 양쪽 공백을 뗀 값
        - path : 4번째 글자부터 끝까지. 이름 바꾸기(' -> ')는 새 이름만.
        - 빈 줄은 건너뛴다. 빈 문자열이 들어오면 [] 를 돌려준다.

    [함정 주의] 줄 전체에 .strip() 을 먼저 하면 ' M' 의 앞 공백이 사라져
    글자 위치가 한 칸씩 밀린다.
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.parse_status_output()')


def get_changed_files(cwd=None):
    """변경된 파일 목록을 돌려준다. 변경이 없으면 [].

    힌트: run_git() 과 parse_status_output() 을 조합한다.
    반환 형식은 parse_status_output() 과 같다.
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.get_changed_files()')


def get_diff(cwd=None):
    """커밋에 들어갈 변경 내용(diff 텍스트)을 돌려준다. 없으면 ''.

    staged(git add 한 것) 변경과 unstaged(아직 git add 안 한 것) 변경을
    "모두" 포함해야 한다.
        git diff --cached  : staged 변경 (다음 커밋에 들어갈 내용)
        git diff           : unstaged 변경

    [생각해 볼 점] git diff 하나만 쓰면 git add 한 뒤에는 diff 가 비어
    "변경 사항이 없습니다"가 잘못 출력될 수 있다.
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.get_diff()')


def count_diff_lines(diff_text):
    """diff 텍스트의 줄 수를 센다. 빈 문자열이면 0.

    로그 출력 예) [INFO] Git diff 수집 완료: 128줄
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.count_diff_lines()')


def get_current_branch(cwd=None):
    """현재 브랜치 이름을 돌려준다. 예) 'feature/add-search'

    PR 초안을 만들 때 [INFO] 현재 브랜치: ... 로 출력하고,
    프롬프트에도 넣어 AI 가 작업 맥락을 알 수 있게 한다.

    힌트: `git branch --show-current` 또는 `git rev-parse --abbrev-ref HEAD`
    """
    # TODO(Step 2): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 2 - git_collector.get_current_branch()')
