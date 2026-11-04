# `ai_gitgen/git_collector.py` — Git 변경 사항 수집

> 실습 단계: 🧩 Step 2 · 자동 테스트: `tests/practice/test_step2_git_collector.py`
> 코드에는 함수마다 한 줄 설명만 두고, 상세 명세는 이 문서에 둔다 (CODYSSEY 코딩 가이드라인 2·7절).

## 1. 모듈의 성격과 역할

Python 에서 `git` 을 실행해 "어떤 파일이 바뀌었는지"(status)와 "무엇이 바뀌었는지"(diff), 현재 브랜치를 얻는다. AI 호출과 분리되어 있어 AI 없이도 이 모듈만 테스트할 수 있고, AI 제공자를 바꿔도 이 파일은 고칠 필요가 없다.

## 2. 포함된 클래스

| 클래스 | 상태 | 설명 |
|---|---|---|
| `GitCommandError` | ✅ 구현됨 | git 명령이 실패했을 때(종료 코드가 0 이 아닐 때) 사용하는 예외. |

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `run_git()` | 🧩 TODO | git 명령을 실행하고 표준 출력(stdout) 문자열을 돌려준다. |
| `is_git_repository()` | 🧩 TODO | cwd 가 Git 저장소(작업 폴더) 안이면 True, 아니면 False. |
| `parse_status_output()` | 🧩 TODO | `git status --porcelain` 출력 문자열을 파일 목록으로 바꾼다. |
| `get_changed_files()` | 🧩 TODO | 변경된 파일 목록을 돌려준다. 변경이 없으면 []. |
| `get_diff()` | 🧩 TODO | 커밋에 들어갈 변경 내용(diff 텍스트)을 돌려준다. 없으면 ''. |
| `count_diff_lines()` | 🧩 TODO | diff 텍스트의 줄 수를 센다. 빈 문자열이면 0. |
| `get_current_branch()` | 🧩 TODO | 현재 브랜치 이름을 돌려준다. 예) 'feature/add-search' |

## 4~6. 함수별 입력·출력과 호출 관계

"명세"는 테스트가 확인하는 약속입니다. 구현 방법(정답)은 들어 있지 않습니다.

### `run_git(args, cwd=None)` — 🧩 TODO

- **누가 호출하나**: `is_git_repository`, `get_changed_files`, `get_diff`, `get_current_branch`
- **다음에 무엇을 호출하나**: `subprocess.run()` (표준)

**명세 (입력 · 출력 · 규칙)**

```text
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
```

### `is_git_repository(cwd=None)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr`
- **다음에 무엇을 호출하나**: `run_git()`

**명세 (입력 · 출력 · 규칙)**

```text
힌트: `git status` 는 저장소 밖에서 실패(오류)한다.
(`git rev-parse --is-inside-work-tree` 도 같은 일을 한다.)
이 함수는 예외를 밖으로 내보내지 말고 True / False 만 돌려준다.

[공식 제약] "Git 변경 사항 수집은 git status, git diff 범위로 제한"
저장소 확인·브랜치 이름은 변경 사항 수집은 아니지만, git status 만으로도
얻을 수 있으니 어느 쪽을 쓸지 정하고 이유를 설명할 수 있게 하자.
```

### `parse_status_output(status_text)` — 🧩 TODO

- **누가 호출하나**: `get_changed_files()`
- **다음에 무엇을 호출하나**: `str.splitlines`, 슬라이싱, `str.split` (기본)

**명세 (입력 · 출력 · 규칙)**

```text
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
```

### `get_changed_files(cwd=None)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr`
- **다음에 무엇을 호출하나**: `run_git()`, `parse_status_output()`

**명세 (입력 · 출력 · 규칙)**

```text
힌트: run_git() 과 parse_status_output() 을 조합한다.
반환 형식은 parse_status_output() 과 같다.
```

### `get_diff(cwd=None)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr`
- **다음에 무엇을 호출하나**: `run_git()` 2번 (`--cached`, 기본)

**명세 (입력 · 출력 · 규칙)**

```text
staged(git add 한 것) 변경과 unstaged(아직 git add 안 한 것) 변경을
"모두" 포함해야 한다.
    git diff --cached  : staged 변경 (다음 커밋에 들어갈 내용)
    git diff           : unstaged 변경

[생각해 볼 점] git diff 하나만 쓰면 git add 한 뒤에는 diff 가 비어
"변경 사항이 없습니다"가 잘못 출력될 수 있다.
```

### `count_diff_lines(diff_text)` — 🧩 TODO

- **누가 호출하나**: `cli.run_commit`, `cli.run_pr` (로그용)
- **다음에 무엇을 호출하나**: `str.splitlines`, `len` (기본)

**명세 (입력 · 출력 · 규칙)**

```text
로그 출력 예) [INFO] Git diff 수집 완료: 128줄
```

### `get_current_branch(cwd=None)` — 🧩 TODO

- **누가 호출하나**: `cli.run_pr`
- **다음에 무엇을 호출하나**: `run_git()`

**명세 (입력 · 출력 · 규칙)**

```text
PR 초안을 만들 때 [INFO] 현재 브랜치: ... 로 출력하고,
프롬프트에도 넣어 AI 가 작업 맥락을 알 수 있게 한다.

힌트: `git status --porcelain --branch` 의 첫 줄 '## 브랜치이름...'
또는 `git branch --show-current`
```

### `GitCommandError` — ✅ 구현됨

- **사용**: `run_git()` 이 raise, `cli.main()` 의 공통 예외 데코레이터가 처리

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수·메서드 | `len`, `str.splitlines`, `str.strip`, `str.split`, 슬라이싱 |
| 표준 라이브러리 | `subprocess` |
| 문법/개념 | `class` (예외 정의), `def`, `try/except`, `raise`, `for`, 리스트·사전 |
| 프로젝트 코드 | `GitCommandError`, `run_git()` 외 7개 함수 |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| `subprocess` | 외부 프로그램 `git` 을 실행하고 출력(stdout)·오류(stderr)·종료 코드를 받기 위해. 외부 패키지 없이 가능 |

## 국소 예외 처리 (가이드라인 5절의 예외적 허용과 이유)

공통 예외는 진입점 `cli.main()` 의 데코레이터에서 한 번에 처리한다. 아래는 하위 계층에서 꼭 필요한 것만 허용한 경우다.

| 함수 | 하는 일 | 이유 |
|---|---|---|
| `run_git()` | `FileNotFoundError`(git 없음)를 `GitCommandError` 로 바꿔 raise | 하위 계층에서 원인이 분명한 예외를 올리기 위해 (가이드라인 5절) |
| `is_git_repository()` | `GitCommandError` 를 잡아 `False` 반환 | "저장소인가?"에 True/False 로 답하는 것이 이 함수의 명세이기 때문 |
