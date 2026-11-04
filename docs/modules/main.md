# `main.py` — 실행 파일(진입점)

> 상태: ✅ 구현됨 · 확인: `tests/base/test_01_environment.py` (`python main.py --help`)

## 1. 모듈의 성격과 역할

프로그램의 시작점이다. `ai_gitgen.cli.main()` 을 부르고 그 반환값을 종료 코드로 쓴다.
학습 중에는 아직 구현하지 않은 TODO 함수가 불릴 수 있으므로, 그때 Traceback 대신
남은 단계를 알려 주는 학습 지원 데코레이터를 진입점에 **한 번만** 붙였다 (가이드라인 5·6절).

## 2. 포함된 클래스

없음.

## 3. 포함된 함수

| 함수 | 상태 | 한 줄 설명 |
|---|---|---|
| `show_todo_hint(func)` | ✅ 구현됨 | [학습 지원] TODO 함수가 불리면 Traceback 대신 남은 단계를 안내한다. |
| `run()` | ✅ 구현됨 | 프로그램을 실행하고 종료 코드(0=정상)를 돌려준다. |

## 4~6. 함수별 입력·출력과 호출 관계

### `show_todo_hint(func)` — ✅ 구현됨

- **입력**: 감쌀 함수 / **출력**: 감싼 함수 (`NotImplementedError` 가 나면 `[TODO]` 안내 두 줄을 출력하고 3 반환)
- **누가 호출하나**: `@show_todo_hint` 로 `run()` 을 정의할 때 Python 이 한 번 부른다
- **다음에 무엇을 호출하나**: 감싼 함수(`run`), `functools.wraps` (표준)

### `run()` — ✅ 구현됨

- **입력**: 없음 (명령줄은 `cli.main()` 이 `sys.argv` 에서 읽는다) / **출력**: 종료 코드
- **누가 호출하나**: `if __name__ == '__main__':` → `sys.exit(run())`
- **다음에 무엇을 호출하나**: `ai_gitgen.cli.main()`

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 기본 함수 | `print` |
| 표준 라이브러리 | `sys`, `functools` |
| 문법/개념 | 데코레이터(`@`), 중첩 함수, `try/except`, `if __name__ == '__main__':` |
| 프로젝트 코드 | `show_todo_hint`, `run`, `ai_gitgen.cli.main` |

## 8. 사용한 주요 표준 라이브러리와 이유

| 라이브러리 | 이유 |
|---|---|
| `sys` | `sys.exit()` 으로 종료 코드를 운영체제에 돌려주기 |
| `functools` | `functools.wraps` — 감싼 뒤에도 원래 함수 이름·설명이 유지되게 하기 |

## 참고: 미션의 공통 예외 처리와의 관계

`show_todo_hint` 는 학습 중에만 의미가 있는 `NotImplementedError` 하나만 다룬다.
미션 실행 중 생기는 `GitCommandError`, `AIClientError` 같은 공통 예외는 Step 7 에서
`cli.main()` 에 붙일 데코레이터에서 처리한다 (`docs/modules/cli.md` 의 "예외 처리 설계").
