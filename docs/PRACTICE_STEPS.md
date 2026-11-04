# B3-2 단계별 실습 워크북 (Step 0 ~ 8)

> 한 번에 전체를 만들지 않습니다. **작은 단계 8개**를 하나씩 끝내고, 단계마다 커밋합니다.
> 그림과 흐름도가 있는 교재: [`docs/B3-2_STUDY_GUIDE.html`](B3-2_STUDY_GUIDE.html) (브라우저로 열기, 인터넷 불필요)
>
> - 명령어의 `python` 은 Mac/Linux 에서 `python3` 일 수 있습니다.
> - **힌트는 정답이 아닙니다.** 다른 예제로 "도구 사용법"만 보여 줍니다.
> - 코드에는 함수마다 한 줄 설명만 있습니다. 입력·출력·규칙(명세)은 `docs/modules/<모듈>.md` 에 있습니다. (CODYSSEY 가이드라인 2·7절)
> - 막히면 순서대로: ① 오류 메시지 첫 줄 읽기 → ② `-v` 로 자세히 보기 → ③ 이 문서의 "오류가 났을 때" → ④ 교재 힌트

## 전체 지도

| 단계 | 만드는 것 | 수정할 파일 | 필수 테스트 수 | 걸리는 시간(예상) |
|---|---|---|---|---|
| 0 | 실습 환경 확인 | (없음) | 기본 테스트 | 20분 |
| 1 | CLI 옵션·입력값 검사 | `ai_gitgen/cli.py` | 12 | 2~3시간 |
| 2 | Git 변경 사항 수집 | `ai_gitgen/git_collector.py` | 18 | 4~5시간 |
| 3 | 안전 모드 (마스킹 필수·전송 제한 선택) | `ai_gitgen/safety.py` | 7 | 3~4시간 |
| 4 | 프롬프트 만들기 | `ai_gitgen/prompt_builder.py` | 11 | 3~4시간 |
| 5 | AI API 요청·응답·오류 처리 | `ai_gitgen/ai_client.py` | 25 | 6~8시간 |
| 6 | 출력 검증·다듬기 | `ai_gitgen/formatter.py` | 21 | 4~5시간 |
| 7 | 전체 흐름 연결 | `ai_gitgen/cli.py` | 16 | 4~6시간 |
| 8 | README·실제 API 1회·제출 | `README.md` | 2 + 직접 확인 | 3~4시간 |

> 필수 테스트 수에는 `(선택)` 테스트가 빠져 있습니다. 선택 테스트는 통과하지 않아도 공식 미션 필수가 아닙니다.

## 모든 단계에서 공통으로 하는 일

```bash
python -m learning_kit.practice          # 진행 현황표: 지금 어느 단계인지
python -m learning_kit.demo N            # Step N 함수 결과를 눈으로 보기 (가짜 AI)
python -m learning_kit.practice N        # Step N 자동 채점
python -m learning_kit.practice N -v     # 실패 원인 자세히
python -m learning_kit.practice base     # 기본 테스트가 계속 통과하는지
```

단계를 끝내면 **커밋**합니다. (커밋 기록과 브랜치 흐름도 제출 기준입니다.)

```bash
git add ai_gitgen/cli.py
git commit -m "feat: CLI 옵션과 입력값 검사 구현"
```

---

## Step 0 · 실습 환경 확인

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | 아무것도 만들지 않습니다. 준비가 되었는지만 확인합니다. |
| 왜 필요한가 | 환경 문제(Python 버전, git 없음)와 코드 문제를 섞지 않기 위해서입니다. |
| 수정할 파일 | 없음 |
| TODO | ① 작업 브랜치 만들기 ② 환경 점검 ③ 연습 저장소 만들어 보기 |

**실행 명령**

```bash
git switch -c feature/my-b3-2          # 내 작업 브랜치 (main 에서 바로 작업하지 않기)
python --version                       # 3.10 이상
git --version
python -m learning_kit.check_env       # 환경 점검 + 기본 테스트
python -m learning_kit.practice_repo   # 연습 저장소 practice_repo/ 만들기
cd practice_repo && git status && git diff && git diff --cached && cd ..
```

**정상 결과**

```
  [OK]   Python 3.12.x (3.10 이상 필요)
  [OK]   git version 2.4x.x
  ...
  필수: 통과 36 / TODO 0 / 실패 0 / 오류 0
  ★ 실습 환경이 준비되었습니다. Step 1 부터 시작하세요.
```

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| `No module named learning_kit` | 프로젝트 폴더(이 파일이 있는 저장소 루트)에서 실행했는지 `pwd` / `cd` 확인 |
| `python: command not found` | `python3` 로 바꿔 실행 (Windows 는 `py`) |
| Python 3.9 이하 | python.org 에서 3.10 이상 설치 |
| git 관련 실패 | Git 설치 후 터미널을 다시 열기 |

**자동 테스트**: `tests/base/` 전체 (`python -m learning_kit.practice base`)

---

## Step 1 · CLI 옵션 만들기·입력값 검사

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | `python main.py commit --temperature 0.2 --max-tokens 300` 같은 명령을 해석하는 **파서**와, 값이 허용 범위 안인지 보는 **검사 함수** |
| 왜 필요한가 | 공식 요구: 모델·temperature·max_tokens 를 **CLI 옵션으로 변경 가능 + 기본값**. 옵션으로 빼 두면 코드를 고치지 않고 같은 조건으로 실험을 반복(재현)할 수 있습니다. 잘못된 값은 AI 를 부르기 **전에** 막아 비용을 아낍니다. |
| 수정할 파일 | `ai_gitgen/cli.py` — `build_parser()`, `validate_options()` · 명세: [`docs/modules/cli.md`](modules/cli.md) |
| 사용하는 것 | 표준 라이브러리 `argparse` / 프로젝트 `config.py` 상수 |

**TODO**

- [ ] `build_parser()` : `commit`, `pr` 하위 명령 만들기 (`args.command` 로 구분)
- [ ] 두 하위 명령 **모두**에 `--model`, `--temperature`(float), `--max-tokens`(int), `--safe-mode`, `--dry-run`(선택) 추가, 기본값은 `config.py`
- [ ] `validate_options(args)` : 범위 밖이면 한국어 문제 메시지를 담은 `list` 반환, 문제 없으면 `[]`

**힌트 (정답 아님 — 다른 예제)**

```python
# 📘 예시: 인사 프로그램. "hello" 하위 명령과 --name 옵션
import argparse

parser = argparse.ArgumentParser(prog='greet')
sub = parser.add_subparsers(dest='command', required=True)
hello = sub.add_parser('hello')
hello.add_argument('--name', default='친구')
hello.add_argument('--times', type=int, default=1)
hello.add_argument('--loud', action='store_true')

args = parser.parse_args(['hello', '--times', '3'])
print(args.command, args.name, args.times, args.loud)   # hello 친구 3 False
```

- 옵션 이름의 `-` 는 결과에서 `_` 로 바뀝니다. (`--max-tokens` → `args.max_tokens`)
- 두 하위 명령에 같은 옵션을 넣는 방법은 두 가지: ① 옵션을 추가하는 작은 함수를 만들어 두 번 부르기 ② `argparse.ArgumentParser(add_help=False)` 로 "공통 부모"를 만들고 `parents=[...]` 로 물려주기
- 범위 검사는 `if not (최소 <= 값 <= 최대):` 모양이 읽기 쉽습니다.

**실행 명령**

```bash
python -m learning_kit.demo 1
python -m learning_kit.demo 1 pr --temperature 0.9 --max-tokens 50
python -m learning_kit.practice 1
```

**정상 결과**

```
>>> build_parser().parse_args(['commit'])
Namespace(command='commit', model='claude-haiku-4-5', temperature=0.3, max_tokens=1024, safe_mode=False, dry_run=False)
>>> validate_options(args)
[]
...
  필수: 통과 12 / TODO 0 / 실패 0 / 오류 0
```

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| `AttributeError: 'Namespace' object has no attribute 'max_tokens'` | 옵션 이름 철자 (`--max-tokens`) |
| `pr --temperature 0.7` 만 실패 | 옵션을 `commit` 에만 붙이지 않았는지 |
| `temperature` 가 문자열 `'0.7'` | `type=float` 를 빠뜨림 |
| 하위 명령 없이도 통과됨 | `add_subparsers(..., required=True)` |

**자동 테스트**: `tests/practice/test_step1_cli_options.py`

**커밋 예**: `feat: CLI 옵션(model/temperature/max-tokens/safe-mode) 추가`

---

## Step 2 · Git 변경 사항 수집

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | Python 에서 `git` 을 실행해 **변경 파일 목록**과 **diff 텍스트**, **현재 브랜치**를 얻는 함수들 |
| 왜 필요한가 | 공식 요구 1: `git status` 로 변경 파일, `git diff` 로 변경 내용. AI 가 읽을 "재료"입니다. AI 호출과 분리하면 AI 없이도 이 부분만 테스트할 수 있습니다. |
| 수정할 파일 | `ai_gitgen/git_collector.py` — 7개 함수 · 명세: [`docs/modules/git_collector.md`](modules/git_collector.md) |
| 사용하는 것 | 표준 라이브러리 `subprocess` / 파이썬 기본 문자열 메서드 `splitlines`, `strip`, `split`, 슬라이싱 |

**TODO** (위에서부터 순서대로)

- [ ] `run_git(args, cwd)` — 실행, 실패하면 `GitCommandError`
- [ ] `is_git_repository(cwd)` — `True` / `False` (예외를 밖으로 내보내지 않기)
- [ ] `parse_status_output(text)` — 문자열 → `[{'code', 'path'}]` (**git 없이 테스트되는 순수 함수**)
- [ ] `get_changed_files(cwd)` — 위 두 함수 조합
- [ ] `get_diff(cwd)` — **staged + unstaged** 둘 다
- [ ] `count_diff_lines(text)`, `get_current_branch(cwd)`

**힌트 (정답 아님)**

```python
# 📘 예시: 다른 프로그램을 실행하고 결과 받기
import subprocess

result = subprocess.run(['python', '--version'], capture_output=True,
                        text=True, encoding='utf-8')
print(result.returncode)   # 0 이면 성공
print(result.stdout)       # 화면에 나왔을 글자
print(result.stderr)       # 오류 글자
```

```python
# 📘 예시: 고정 폭 문자열 자르기
line = 'AB hello.txt'
print(repr(line[:2]))      # 'AB'
print(repr(line[3:]))      # 'hello.txt'
print(repr('  x '.strip()))  # 'x'  ← 앞 공백도 사라진다!
```

- `git status --porcelain` 의 각 줄: **앞 2글자 = 상태 코드, 3번째 = 공백, 4번째부터 = 경로**
- `' M app.py'` 를 먼저 `.strip()` 하면 `'M app.py'` 가 되어 위치가 한 칸 밀립니다.
- 이름 바꾸기 줄: `R  old.md -> new.md` → `' -> '` 로 나눠 마지막 것
- `cwd` 는 `subprocess.run(..., cwd=cwd)` 로 그대로 넘기면 됩니다. (`None` 이면 현재 폴더)
- 공식 제약은 "변경 사항 수집은 `git status`, `git diff` 범위"입니다. 저장소 확인은 `git status` 의 성공/실패로, 브랜치 이름은 `git status --porcelain --branch` 첫 줄(`## 브랜치이름...`)로도 얻을 수 있습니다. `git rev-parse`·`git branch` 를 써도 테스트는 통과하지만, 어느 쪽을 골랐는지와 이유를 설명할 수 있게 하세요.
- 연습 저장소에서 직접 비교: `git diff` 와 `git diff --cached` 의 결과가 어떻게 다른지 먼저 눈으로 보세요.

**실행 명령**

```bash
python -m learning_kit.practice_repo feature     # 연습 저장소 새로 만들기
python -m learning_kit.demo 2
python -m learning_kit.practice 2
```

**정상 결과**

```
>>> get_changed_files()
[{'code': 'M', 'path': 'README.md'}, {'code': 'M', 'path': 'todo_app/app.py'}, {'code': 'A', 'path': 'todo_app/search.py'}]
>>> count_diff_lines(diff)
46
  필수: 통과 18 / TODO 0 / 실패 0 / 오류 0
```

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| 경로 첫 글자가 잘림 (`odo_app/app.py`) | 줄 전체를 먼저 `.strip()` 했는지 |
| `test_staged_change_is_included` 실패 | `git diff --cached` 를 빠뜨림 |
| `is_git_repository` 에서 예외 | `try / except GitCommandError` 로 `False` 반환 |
| 한글이 깨짐 (Windows) | `encoding='utf-8'` 지정, 파일명은 `git -c core.quotepath=false ...` |
| `FileNotFoundError: 'git'` | git 설치 확인. 이 예외도 `GitCommandError` 로 바꾸기 |

**자동 테스트**: `tests/practice/test_step2_git_collector.py` (임시 폴더에 진짜 Git 저장소를 만들어 확인)

---

## Step 3 · 안전 모드: 마스킹·전송 제한

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | diff 안의 API Key·이메일 등을 `[MASKED]` 로 가리는 함수 (A), (선택) diff 를 최대 10파일·200줄로 자르는 함수 (B), 이를 묶는 `--safe-mode` 함수 |
| 왜 필요한가 | 공식 제약: diff 속 민감정보를 프롬프트에 넣지 않도록 (A) 마스킹 또는 (B) 일부만 전송 중 **1개 이상**. 이 실습은 (A)를 필수, (B)를 선택으로 둡니다. (B)까지 하면 보내는 양이 줄어 **비용**도 줄어듭니다. |
| 수정할 파일 | `ai_gitgen/safety.py` — `SENSITIVE_PATTERNS`, `mask_sensitive()`, `limit_diff()`, `apply_safe_mode()` · 명세: [`docs/modules/safety.md`](modules/safety.md) |
| 사용하는 것 | 표준 라이브러리 `re` (정규표현식) |

**TODO**

- [ ] `SENSITIVE_PATTERNS` 채우기: ① `sk-` 로 시작하는 긴 키 ② 이메일 — (선택) `api_key`·`secret`·`token`·`password` 뒤 `=`/`:` 로 이어지는 값, 휴대전화
- [ ] `mask_sensitive(text)` — 패턴을 돌며 바꾸기. **민감정보가 아닌 글자는 그대로**
- [ ] (선택) `limit_diff(diff, max_files, max_lines)` — 파일 수 제한 → 줄 수 제한 → (잘랐다면) 안내 1줄
- [ ] `apply_safe_mode(diff, enabled)` — 마스킹(필수) + `limit_diff` 를 구현했다면 전송 제한

**힌트 (정답 아님)**

```python
# 📘 예시: 주문번호(숫자 5자리)를 가리기
import re

text = '주문번호 12345, 문의 00000'
print(re.sub(r'\d{5}', '[숨김]', text))            # 주문번호 [숨김], 문의 [숨김]
print(re.sub(r'(?i)order', 'ORDER', 'Order order'))  # (?i) = 대소문자 무시
print(re.sub(r'(번호 )\d+', r'\1[숨김]', text))      # \1 = 괄호로 묶은 부분은 살리기
```

| 정규식 조각 | 뜻 |
|---|---|
| `[A-Za-z0-9_-]` | 영문·숫자·`_`·`-` 중 한 글자 |
| `{16,}` | 앞의 것이 16번 이상 |
| `\s*` | 공백 0개 이상 |
| `[:=]` | `:` 또는 `=` |
| `['"]?` | 따옴표가 있어도 되고 없어도 됨 |
| `[^'"\s]+` | 따옴표·공백이 아닌 글자 1개 이상 |
| `(?i)` | 대소문자 무시 |

- 파일 단위 자르기: `'diff --git '` 으로 시작하는 줄을 만날 때마다 "파일 수 + 1"
- `splitlines(keepends=True)` 를 쓰면 줄바꿈을 잃지 않고 다시 `''.join(...)` 할 수 있습니다.
- 정규식 실험은 `python` 대화형 모드에서 짧게 여러 번 해 보세요.

**실행 명령**

```bash
python -m learning_kit.demo 3
python -m learning_kit.practice 3
python -m learning_kit.practice_repo secret   # 가짜 비밀이 든 연습 저장소
```

**정상 결과**

```
+API_KEY = "[MASKED]"
+ADMIN_EMAIL = "[MASKED]"
...
  -> 결과 줄 수: 201, 파일 수: 7      (선택: limit_diff 를 구현한 경우)
  필수: 통과 7 / TODO 0 / 실패 0 / 오류 0
```

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| `test_normal_code_is_unchanged` 실패 | 패턴이 너무 넓음 (예: `title` 까지 가림) |
| (선택) `DB_PASSWORD` 가 안 가려짐 | 이름 앞에 다른 글자(`DB_`)가 붙어도 찾는지, 대소문자 무시 |
| 줄 수가 바뀜 | 패턴이 줄바꿈 `\n` 까지 먹지 않는지 (`\s` 는 줄바꿈 포함!) |
| (선택) 10파일이 넘게 남음 | 11번째 `diff --git` 줄에서 멈추는지 |

**자동 테스트**: `tests/practice/test_step3_safety.py`

---

## Step 4 · 프롬프트 만들기

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | 변경 파일 목록 + diff + 규칙을 담은 **AI 요청문(문자열)** 2종 (커밋용, PR용) |
| 왜 필요한가 | 미션의 핵심 "어떤 입력을 주냐". AI 는 시킨 것만 압니다. 형식·길이·언어·섹션을 알려 줘야 원하는 결과가 나옵니다. |
| 수정할 파일 | `ai_gitgen/prompt_builder.py` — `format_file_list()`, `build_commit_prompt()`, `build_pr_prompt()` · 명세: [`docs/modules/prompt_builder.md`](modules/prompt_builder.md) |
| 사용하는 것 | 파이썬 기본 f-string, `'\n'.join()` / 프로젝트 `config.py` 상수 |

**TODO**

- [ ] `format_file_list(files)` — `- [M] app.py` 같은 줄 목록, 빈 목록이면 안내 문구
- [ ] `build_commit_prompt(files, diff)` — 역할, 출력 형식, 제목 길이(50/72), 접두어(feat/fix/docs…), 언어, 파일 목록, diff
- [ ] `build_pr_prompt(files, diff, branch)` — 위 + 브랜치, 제목 80자, `## Why` / `## What` / `## How to Test` + 불릿

**힌트 — 프롬프트에 넣을 정보 체크리스트**

| 정보 | 왜 | 넣었나 |
|---|---|---|
| 역할 ("너는 커밋 메시지를 쓰는 도우미다") | 답의 관점을 고정 | ☐ |
| 출력 형식 (첫 줄 제목, 빈 줄, 불릿) | 받은 뒤 나누기 쉬움 | ☐ |
| 길이 규칙 숫자 (50/72, 80) | 규칙 위반 줄이기 | ☐ |
| 접두어 규칙 (feat/fix/docs/refactor/test) | 팀 컨벤션 | ☐ |
| 출력 언어 (한국어) | 섞이지 않게 | ☐ |
| 하지 말 것 (설명 문장, ``` 감싸기) | 후처리 줄이기 | ☐ |
| 변경 파일 목록 | 무엇이 바뀌었나 | ☐ |
| diff | 어떻게 바뀌었나 | ☐ |
| (PR) 브랜치 이름 | 작업 맥락 | ☐ |

```python
# 📘 예시: 여러 줄 문자열 만들기 (내용은 미션과 무관)
items = ['사과', '배']
lines = '\n'.join(f'- {item}' for item in items)
text = (
    '너는 장보기 도우미다.\n'
    f'목록:\n{lines}\n'
)
print(text)
```

- 시간·난수(`datetime.now()`, `random`)를 넣지 마세요. 같은 입력이면 같은 프롬프트여야 실험을 반복할 수 있습니다.
- 프롬프트 글자 수가 늘면 입력 토큰(비용)도 늘어납니다. 데모가 글자 수를 보여 줍니다.

**실행 명령**

```bash
python -m learning_kit.demo 4
python -m learning_kit.practice 4
```

**정상 결과**: 데모에 내가 만든 프롬프트 전문과 `[INFO] 커밋 프롬프트: ...글자` 가 보이고, `필수: 통과 11`

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| `test_contains_paths_and_diff` 실패 | diff 를 잘라 넣거나 바꾸지 않았는지 (자르기는 Step 3 담당) |
| `test_is_deterministic` 실패 | 시간·난수 사용 |
| `KeyError: 'path'` | 파일 목록 항목이 사전 `{'code', 'path'}` 인지 |

**자동 테스트**: `tests/practice/test_step4_prompt.py`

---

## Step 5 · AI API 요청·응답·오류 처리

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | 환경변수에서 키 읽기 → 헤더·본문 만들기 → HTTP POST → 응답 JSON 에서 글자 꺼내기, 그리고 **모든 실패를 `AIClientError` 로 바꾸기** |
| 왜 필요한가 | 공식 요구 2: 키는 환경변수, 실패 시 **원인을 포함한** 메시지. REST API 의 요청·응답·예외 흐름을 말로 설명할 수 있어야 합니다(과제 목표 1). |
| 수정할 파일 | `ai_gitgen/ai_client.py` — 6개 함수 · 명세: [`docs/modules/ai_client.md`](modules/ai_client.md) |
| 사용하는 것 | 표준 라이브러리 `os`, `json`, `urllib.request`, `urllib.error` |

**TODO**

- [ ] `get_api_key()` — 없거나 공백이면 `MissingApiKeyError` (메시지에 환경변수 **이름**과 설정 예시, 값은 절대 X)
- [ ] `build_headers(api_key, provider)` — anthropic: `x-api-key`·`anthropic-version`, openai: `Authorization: Bearer` (필수는 `config.DEFAULT_PROVIDER` 형식 하나, 다른 형식은 선택)
- [ ] `build_request_body(...)` — `model`, `max_tokens`, `temperature`, `messages`
- [ ] `extract_text(data, provider)` — anthropic 은 `content` 목록 중 `type == 'text'` 만! 모양이 다르면 `AIClientError`
- [ ] `send_http_request(url, headers, body, timeout)` — HTTPError(상태 코드) / URLError(원인) / TimeoutError / JSON 오류
- [ ] `call_ai_api(...)` — 키 → 헤더·본문 → `transport(...)` **1회** → `extract_text`

**힌트 (정답 아님)**

```python
# 📘 예시: 환경변수 읽기
import os
home = os.environ.get('HOME', '')       # 없으면 '' (KeyError 안 남)
```

```python
# 📘 예시: JSON ↔ 사전
import json
data = {'name': '홍길동', 'items': [1, 2]}
text = json.dumps(data, ensure_ascii=False)   # 사전 → 문자열
raw = text.encode('utf-8')                    # 문자열 → 바이트 (HTTP 로 보낼 때)
back = json.loads(raw.decode('utf-8'))        # 바이트 → 사전
```

```python
# 📘 예시: 예외를 "우리 예외"로 바꾸기 (except 순서 = 구체적인 것 먼저)
class MyError(Exception):
    pass

try:
    int('abc')
except ValueError as error:
    raise MyError(f'숫자가 아닙니다: {error}') from error
```

- `urllib.request.Request(url, data=바이트, headers=사전, method='POST')` 를 만들어 `urllib.request.urlopen(요청, timeout=...)` 에 넘깁니다. **반드시 `urllib.request.urlopen` 형태로** 부르세요. (테스트가 이 함수를 가짜로 바꿉니다.)
- `urllib.error.HTTPError` 는 `URLError` 의 **자식**입니다. 어느 쪽을 먼저 `except` 해야 할까요?
- openai 형식의 일부 최신(추론) 모델은 `max_tokens` 대신 `max_completion_tokens` 를 요구하고 temperature 를 바꿀 수 없습니다. 테스트는 openai 형식에서 두 이름을 모두 인정합니다.
- `HTTPError` 객체: `error.code` (상태 코드), `error.read()` (오류 본문 바이트)
- 응답 예시 파일: `practice_data/api_responses/*.json` — 직접 열어 모양을 보세요.

| HTTP 상태 | 뜻 | 사용자에게 알려 줄 것 |
|---|---|---|
| 400 | 잘못된 요청 (예: 모델이 temperature 를 거부) | 옵션·모델 확인 |
| 401 | 인증 실패 (키 틀림) | 키 다시 설정 |
| 403 | 권한 없음 | 계정 권한 |
| 404 | 주소·모델 이름 틀림 | `--model` 철자 |
| 429 | 요청이 너무 많음 | 잠시 후 다시 |
| 500 / 529 | 서버 문제 / 과부하 | 잠시 후 다시 |

**실행 명령**

```bash
python -m learning_kit.demo 5       # 가짜 AI 로 요청·응답 보기 (실제 호출 없음)
python -m learning_kit.practice 5
```

**정상 결과**

```
[INFO] 가짜 AI 호출 횟수: 1
[INFO] 보낸 주소: https://api.anthropic.com/v1/messages
[INFO] 보낸 헤더(키는 *** 로 가림): {'x-api-key': '***', ...}
>>> get_api_key()  (환경변수 없음 -> MissingApiKeyError 예상)
예상대로 MissingApiKeyError: AI_API_KEY 환경변수가 설정되지 않았습니다. ...
  필수: 통과 25 / TODO 0 / 실패 0 / 오류 0
```

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| `RuntimeError: 테스트 중에는 실제 네트워크 ... 금지` | `call_ai_api` 가 `transport` 를 무시하고 직접 통신함 |
| `test_default_provider_response` 실패 (anthropic) | `content[0]['text']` 로 꺼냄 → `type` 확인 필요 |
| `KeyError` 가 그대로 보임 | `try/except (KeyError, IndexError, TypeError)` → `AIClientError` |
| 401 테스트에 `'401'` 없음 | `except URLError` 가 `HTTPError` 보다 먼저 있음 |
| `TypeError: POST data should be bytes` | `json.dumps(...).encode('utf-8')` |

**자동 테스트**: `tests/practice/test_step5_ai_client.py` (가짜 transport + 가짜 urlopen)

---

## Step 6 · 출력 검증·다듬기

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | AI 글을 제목/본문으로 나누고, 길이·형식 규칙을 검사하고, 구획을 나눠 출력하는 함수들 |
| 왜 필요한가 | 공식 요구 5: 커밋 제목 50(72)자, PR 제목 80자, PR 섹션·불릿 규칙 + 구분선. AI 는 규칙을 가끔 어기므로 받은 뒤 **프로그램이 다시 확인**합니다. |
| 수정할 파일 | `ai_gitgen/formatter.py` — 7개 함수 · 명세: [`docs/modules/formatter.md`](modules/formatter.md) |
| 사용하는 것 | 파이썬 기본 `len`, `str.splitlines`, `str.strip`, `str.startswith`, 슬라이싱 / `config.py` |

**TODO**

- [ ] `split_title_body(text)` → `(제목, 본문)`
- [ ] `shorten_title(title, max_length)` — 결과 길이 ≤ max_length
- [ ] `validate_commit_message(message, changed_paths)` — 빈 제목, 72자 초과, 본문에 불릿·파일 언급 없음
- [ ] `validate_pr_title(title)`, `validate_pr_body(body)` — 섹션 헤더 + 섹션별 불릿
- [ ] `format_commit_output(message)`, `format_pr_output(title, body)` — 헤더·구분선

**힌트 (정답 아님)**

```python
# 📘 예시: 문자열 다루기
text = '\n\n  첫째 줄  \n둘째 줄\n'
lines = text.strip().splitlines()      # ['첫째 줄  ', '둘째 줄'] (strip 은 양끝만)
print(len('가나다'))                     # 3  ← 글자 수
print('abcdef'[:4])                     # 'abcd'
print('## Why (배경)'.lstrip('#').strip().startswith('Why'))   # True
print('- 항목'.startswith(('- ', '* ')))  # True  ← 튜플로 여러 개 확인
```

- PR 본문 검사는 "지금 어떤 섹션 안에 있는지"를 변수에 기억하면서 한 줄씩 읽으면 쉽습니다.
- 출력 형식 예: `practice_data/expected_outputs/*.txt`
- **재생성 vs 후처리** 중 무엇을 고를지 이 단계에서 정하고, 이유를 `MY_ANSWERS.md` 에 적어 두세요.

**실행 명령**

```bash
python -m learning_kit.demo 6
python -m learning_kit.practice 6
```

**정상 결과**

```
[INFO] 긴 제목 길이: 121글자
>>> shorten_title(긴 제목, 72)
  -> 줄인 뒤 길이: 72글자 이하
>>> validate_pr_body(섹션 빠진 본문)
['What 섹션에 불릿이 없습니다.', 'How to Test 섹션이 없습니다.']
  필수: 통과 21 / TODO 0 / 실패 0 / 오류 0
```

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| 줄인 제목이 73자 | `'...'` 를 붙인 뒤 길이까지 계산했는지 |
| `## What` 이 `Why` 섹션으로 잡힘 | 헤더를 만나면 "현재 섹션"을 바꾸는지 |
| 51~72자 제목이 문제로 나옴 | 72자 **초과**만 문제 (50은 권장) |
| `line_after` 관련 실패 | 헤더 줄 **다음 줄**에 제목이 오는지 |

**자동 테스트**: `tests/practice/test_step6_formatter.py`

---

## Step 7 · 전체 흐름 연결 (commit / pr)

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | Step 1~6 함수를 순서대로 부르는 `run_commit()`, `run_pr()`, `main()` |
| 왜 필요한가 | 공식 결과물 ①: **한 번 실행으로 자동화 흐름이 끝까지 동작**. 체크리스트 항목 1 의 대부분을 여기서 만족합니다. |
| 수정할 파일 | `ai_gitgen/cli.py` — `run_commit()`, `run_pr()`, `main()` · 명세: [`docs/modules/cli.md`](modules/cli.md) |
| 사용하는 것 | 프로젝트 함수 전부 + `log()` (✅ 구현됨) |

**TODO**

- [ ] `main(argv, cwd, transport)` — 파싱 → 검사(문제 있으면 `[ERROR]` 후 2) → commit/pr 로 보내기
- [ ] `run_commit(args, cwd, transport)` — 교재 '커밋 메시지 생성 흐름' 8단계
- [ ] `run_pr(args, cwd, transport)` — 브랜치 로그 포함
- [ ] 모든 단계에 `cwd` 와 `transport` 를 **끝까지 넘기기**
- [ ] 공통 예외(`GitCommandError`, `AIClientError`)는 `main()` 위에 붙인 **데코레이터 한 곳**에서 `[ERROR]` + 원인·해결 힌트 + 종료 코드 1 — `run_commit`/`run_pr` 에서 같은 `try/except` 를 반복하지 않기 (가이드라인 5·6절, 설계 표: `docs/modules/cli.md`)
- [ ] AI 호출 횟수 로그 (`[DONE] ... (API 호출 1회)`)
- [ ] (선택) `--dry-run`: 프롬프트만 출력하고 0

**힌트 — 흐름을 말로 먼저 쓰기 (코드 아님)**

```
run_commit:
  저장소인가? ─아니오→ [ERROR] → 1
  변경 파일 목록 ─비었음→ [INFO] 변경 사항이 없습니다 → 0
  diff 수집 → [INFO] n줄
  safe-mode 면 → 안전하게
  프롬프트 만들기 ─dry-run→ 출력 → 0
  키 확인 ─없음→ [ERROR] AI_API_KEY ... → 1
  AI 1회 호출 ─실패→ [ERROR] 원인 → 1
  제목/본문 나누기 → 규칙 적용 → 문제는 [WARN]
  구획 나눠 출력 → 0
```

- `main.py` 는 `main()` 을 인자 없이 부릅니다. `argv=None` 이면 `parse_args(None)` 이 실제 명령줄을 읽습니다.
- 실제로 동작하는 데코레이터 예는 `main.py` 의 `show_todo_hint` 입니다. `functools.wraps` 를 쓰면 감싼 뒤에도 `main` 의 매개변수가 유지되어 기본 테스트(함수 약속)가 계속 통과합니다.
- `run_commit` 과 `run_pr` 의 공통 부분(변경 수집 → safe-mode → AI 호출)은 공통 함수로 분리해 중복을 줄이세요 (가이드라인 3절).
- 출력 예: `practice_data/expected_outputs/` 의 세 파일

**실행 명령**

```bash
python -m learning_kit.demo 7                  # 가짜 AI 로 5가지 상황 모의 실행
python -m learning_kit.practice 7
python -m learning_kit.practice_repo feature
cd practice_repo
python ../main.py commit --dry-run             # (선택 구현 시) AI 없이 프롬프트 확인
python ../main.py commit                       # 키가 없으면 [ERROR] AI_API_KEY ...
cd ..
```

**정상 결과**: 데모에서 5가지 상황(commit, pr, 변경 없음, 키 없음, safe-mode)의 출력과 `가짜 AI 호출 횟수` 가 기대대로 나오고, `필수: 통과 16`

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| `RuntimeError: ... 네트워크 ... 금지` | `transport` 를 `call_ai_api` 까지 넘겼는지 |
| 변경 없음인데 AI 호출 1회 | 변경 확인을 AI 호출보다 먼저 하는지 |
| `[ERROR]` 가 안 보임 | 예외를 잡아 `log('ERROR', ...)` 했는지 (`ERROR` 는 stderr 로 출력됨) |
| 다른 폴더의 저장소를 읽음 | `cwd` 를 Git 함수에 넘겼는지 |
| `--temperature 5` 인데 AI 호출됨 | `validate_options` 를 호출 전에 실행했는지 |

**자동 테스트**: `tests/practice/test_step7_flow.py`

---

## Step 8 · README 작성·실제 API 1회 확인·제출

| 항목 | 내용 |
|---|---|
| 무엇을 만드는가 | 제출용 `README.md`, 실제 API 결과 1~2회 기록, 설명 답안(`MY_ANSWERS.md`) |
| 왜 필요한가 | 공식 결과물 ②③ + 체크리스트 항목 1 의 "temperature/max-tokens 차이 재현", 항목 2~4 설명 |
| 수정할 파일 | `README.md` (틀: `docs/templates/README_TEMPLATE.md`), `docs/templates/MY_ANSWERS.md` |

**TODO**

- [ ] `README.md` 를 템플릿으로 다시 쓰고 `TODO(Step 8)` 표시 지우기
- [ ] API Key 발급 → **터미널에서만** 환경변수 설정 (파일에 쓰지 않기)
- [ ] 실제 실행 (총 2~4회 이내 권장)
  - `python main.py commit --dry-run` 으로 보낼 내용 먼저 확인
  - `python main.py commit` 1회
  - `python main.py pr` 1회
  - (실험) `--max-tokens 60` vs `--max-tokens 600` 비교 1회씩 — 또는 temperature 0.0 vs 1.0
- [ ] 결과를 README 출력 예시에 붙이기 (키·개인정보 없는지 확인)
- [ ] `python -m learning_kit.practice base` 다시 통과 확인 (키가 파일에 없는지)
- [ ] 작업 브랜치 push → GitHub 에서 파일 구조·커밋 기록 확인

**환경변수 설정 (현재 터미널에서만 유지)**

```bash
# Mac / Linux
export AI_API_KEY="여기에_발급받은_키"
# Windows PowerShell
$env:AI_API_KEY="여기에_발급받은_키"
# Windows 명령 프롬프트(cmd)
set AI_API_KEY=여기에_발급받은_키
```

> ⚠️ 키를 README·코드·커밋 메시지·스크린샷에 넣지 마세요. 실수로 커밋했다면 **즉시 제공자 사이트에서 키를 폐기(재발급)** 하세요. 커밋을 지워도 기록이 남을 수 있습니다.

**실행 명령**

```bash
python -m learning_kit.demo 8        # README 필수 내용 점검표
python -m learning_kit.practice 8
python -m learning_kit.practice      # 전체 진행 현황 — 모두 '완료'
```

**정상 결과**: 진행 현황표의 8단계가 모두 `완료`, 실제 실행 결과가 README 에 있음

**오류가 났을 때 확인할 내용**

| 증상 | 확인 |
|---|---|
| HTTP 400 + temperature 관련 메시지 | 그 모델은 temperature 를 바꿀 수 없음 → 기본값만 받는 모델(예: Claude Haiku 5.5)은 `--temperature 1.0`, 아니면 temperature 를 받는 모델로 바꾸거나 max-tokens 로 실험 |
| HTTP 400 + `max_tokens` 관련 (openai) | 최신 모델은 `max_completion_tokens` 라는 이름을 요구 |
| HTTP 401 | 키 철자, 따옴표, 다른 터미널 창에서 설정하지 않았는지 |
| HTTP 404 | `--model` 이름 철자 |
| HTTP 429 | 잠시 기다린 뒤 다시 (반복 실행 금지) |
| 출력이 중간에 끊김 | `max_tokens` 가 너무 작음 (응답의 `stop_reason` 확인) |
| "응답에 글자가 없다"는 오류 | 최신 모델은 답을 쓰기 전에 생각(thinking)에 토큰을 먼저 씀 → `max_tokens` 를 늘려 보기 |

**자동 테스트**: `tests/practice/test_step8_readme.py` + `tests/base/test_05_security.py`

---

## 다 끝냈다면

1. `docs/templates/MY_ANSWERS.md` 의 질문에 내 말로 답하기 (체크리스트 항목 2~4)
2. 교재의 '30초 프로그램 설명 연습'을 소리 내어 3번
3. (선택) 보너스 과제 — `docs/REQUIREMENTS_ANALYSIS.md` 2-3절
