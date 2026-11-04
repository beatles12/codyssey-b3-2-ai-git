"""명령줄(CLI) 처리와 전체 흐름 연결.

[실습 단계]
    🧩 Step 1  build_parser(), validate_options()
    🧩 Step 7  run_commit(), run_pr(), main()

[이 파일이 하는 일]
    사용자가 터미널에 입력한 `python main.py commit --temperature 0.2` 같은
    명령을 해석하고, 다른 모듈의 함수를 순서대로 불러 결과를 출력한다.

[자주 쓰는 표준 라이브러리]
    argparse : 명령줄 옵션 해석
    sys      : 표준 출력/표준 오류(sys.stdout / sys.stderr)
"""

import argparse  # noqa: F401  (Step 1 에서 사용합니다)
import sys

from ai_gitgen import config  # noqa: F401  (Step 1, Step 7 에서 사용합니다)


# ---------------------------------------------------------------------------
# ✅ 구현됨 — 출력 형식 예시
# ---------------------------------------------------------------------------
def log(level, message):
    """머리표([INFO], [DONE], [WARN], [ERROR])를 붙여 한 줄을 출력한다.

    예)
        log('INFO', 'AI API 요청 중...')  ->  [INFO] AI API 요청 중...

    [ERROR] 는 표준 오류(sys.stderr)로, 나머지는 표준 출력으로 보낸다.
    이렇게 나누면 정상 결과와 오류 메시지를 따로 저장하거나 볼 수 있다.
    """
    stream = sys.stderr if level == 'ERROR' else sys.stdout
    print(f'[{level}] {message}', file=stream)


# ---------------------------------------------------------------------------
# 🧩 Step 1 — 명령줄 옵션 만들기
# ---------------------------------------------------------------------------
def build_parser():
    """commit / pr 하위 명령과 공통 옵션을 가진 ArgumentParser 를 만든다.

    반환값
        argparse.ArgumentParser

    만들어야 하는 명령 형태
        python main.py commit [옵션]
        python main.py pr     [옵션]

    두 하위 명령에 모두 있어야 하는 옵션 (하위 명령 "뒤"에 쓸 수 있어야 함)
        --model        문자열, 기본값 config.DEFAULT_MODEL
        --temperature  실수(float), 기본값 config.DEFAULT_TEMPERATURE
        --max-tokens   정수(int),  기본값 config.DEFAULT_MAX_TOKENS
                       (parse_args 결과에서는 args.max_tokens 로 읽힌다)
        --safe-mode    켜기/끄기(store_true), 기본값 False
        --dry-run      켜기/끄기(store_true), 기본값 False   [권장·선택]
                       AI 를 부르지 않고 "보낼 프롬프트"만 보여 주는 모드

    parse_args 결과(Namespace)에서 확인하는 값
        args.command      'commit' 또는 'pr'
        args.model, args.temperature, args.max_tokens,
        args.safe_mode, args.dry_run

    테스트가 확인하는 것 (tests/practice/test_step1_cli_options.py)
        - 하위 명령 없이 실행하면 SystemExit 이 발생한다.
        - --max-tokens abc 처럼 숫자가 아니면 SystemExit 이 발생한다.
    """
    # TODO(Step 1): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 1 - cli.build_parser()')


def validate_options(args):
    """parse_args 로 얻은 옵션 값이 허용 범위 안에 있는지 검사한다.

    매개변수
        args : build_parser().parse_args(...) 의 결과

    반환값
        list[str] : 문제를 설명하는 한국어 메시지 목록. 문제가 없으면 [].

    검사 규칙 (범위 값은 config.py 에 있음)
        - temperature 가 TEMPERATURE_MIN ~ TEMPERATURE_MAX 를 벗어나면
          'temperature' 라는 단어가 들어간 메시지를 추가한다.
        - max_tokens 가 MAX_TOKENS_MIN ~ MAX_TOKENS_LIMIT 를 벗어나면
          'max' 라는 단어가 들어간 메시지를 추가한다. (예: --max-tokens)
        - model 이 빈 문자열이면 'model' 이 들어간 메시지를 추가한다.

    왜 필요할까?
        잘못된 값으로 AI API 를 부르면 돈(토큰)과 시간을 쓴 뒤에야
        오류를 알게 된다. 보내기 "전에" 검사하면 비용 없이 막을 수 있다.
    """
    # TODO(Step 1): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 1 - cli.validate_options()')


# ---------------------------------------------------------------------------
# 🧩 Step 7 — 전체 흐름 연결
# ---------------------------------------------------------------------------
def run_commit(args, cwd=None, transport=None):
    """`commit` 명령의 전체 흐름을 실행하고 종료 코드를 돌려준다.

    매개변수
        args      : parse_args 결과
        cwd       : Git 명령을 실행할 폴더 (None 이면 현재 폴더)
        transport : 테스트용 가짜 통신 함수. ai_client.call_ai_api() 에
                    그대로 넘긴다. (None 이면 실제 HTTP 통신)

    반환값 (종료 코드)
        0 : 정상 완료, 또는 "변경 사항이 없습니다" 안내 후 종료
        1 : Git 저장소가 아님 / API Key 없음 / API 호출 실패 등 오류

    권장 흐름 (교재의 '커밋 메시지 생성 흐름' 그림 참고)
        1) Git 저장소인지 확인 -> 아니면 [ERROR]
        2) 변경 파일 목록 수집 -> 없으면 [INFO] 변경 사항이 없습니다 ... 후 0
        3) diff 수집 -> 줄 수를 [INFO] 로 출력
        4) --safe-mode 면 마스킹/전송 제한 적용
        5) 커밋용 프롬프트 만들기 (--dry-run 이면 여기서 출력하고 0)
        6) AI API 1회 호출 (호출 횟수를 로그로 출력)
        7) 제목/본문 나누기 -> 길이 규칙 적용 -> 검증 결과는 [WARN]
        8) format_commit_output() 으로 구획을 나눠 출력

    테스트가 확인하는 것 (tests/practice/test_step7_flow.py)
        - 변경이 없으면 AI 를 부르지 않는다.
        - API Key 가 없으면 AI 를 부르지 않고 'AI_API_KEY' 를 안내한다.
        - 정상일 때 AI 호출은 정확히 1회다.
        - 출력된 커밋 제목은 72자 이하다.
    """
    # TODO(Step 7): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 7 - cli.run_commit()')


def run_pr(args, cwd=None, transport=None):
    """`pr` 명령의 전체 흐름을 실행하고 종료 코드를 돌려준다.

    run_commit() 과 거의 같지만 다음이 다르다.
        - 현재 브랜치 이름을 [INFO] 로 출력하고 프롬프트에 넣는다.
        - AI 응답의 첫 줄을 PR 제목, 나머지를 PR 본문으로 쓴다.
        - PR 제목은 80자 이하, 본문은 Why / What / How to Test 섹션과
          섹션마다 1개 이상의 불릿(- )이 있어야 한다.
        - format_pr_output() 으로 구획을 나눠 출력한다.

    길이/형식 규칙을 지키는 방법은 둘 중 하나를 고른다 (공식 요구사항).
        (가) 후처리: 프로그램이 직접 자르고 다듬는다. (추가 비용 없음)
        (나) 재생성: 규칙을 어기면 1번만 더 요청한다. (호출 최대 2회)
    """
    # TODO(Step 7): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 7 - cli.run_pr()')


def main(argv=None, cwd=None, transport=None):
    """프로그램 시작점. 옵션을 해석하고 commit / pr 흐름으로 보낸다.

    매개변수
        argv      : 옵션 목록 (None 이면 실제 명령줄 sys.argv[1:] 사용)
                    예) ['commit', '--temperature', '0.2']
        cwd       : run_commit / run_pr 에 그대로 넘긴다.
        transport : run_commit / run_pr 에 그대로 넘긴다.

    반환값 (종료 코드)
        run_commit / run_pr 의 반환값.
        validate_options() 가 문제를 찾으면 [ERROR] 로 알리고 2 를 반환
        (AI 는 부르지 않는다).
    """
    # TODO(Step 7): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 7 - cli.main()')
