"""프롬프트 구성 — AI 에게 보낼 요청문(문자열)을 만든다.

[실습 단계] 🧩 Step 4

[미션의 핵심]
    "AI API 연동의 핵심은 '어떤 입력을 주냐'에 있다." (공식 미션 소개)
    같은 diff 라도 어떤 규칙과 맥락을 함께 주느냐에 따라 결과 품질이 달라진다.

[왜 출력 다듬기(formatter.py)와 분리할까?]  (공식 체크리스트 항목 2)
    - 프롬프트는 "AI 에게 부탁하는 내용", 출력 다듬기는 "받은 결과를
      검사하고 고치는 내용"이다.
    - AI 는 부탁을 100% 지키지 않을 수 있으므로, 받은 뒤 검사하는
      단계가 따로 있어야 한다.

[이 파일의 함수는 순수 함수로 만든다]
    입력이 같으면 항상 같은 문자열을 돌려줘야 한다. (시간·난수 금지)
    그래야 테스트할 수 있고, 같은 조건으로 실험을 반복(재현)할 수 있다.
"""

from ai_gitgen import config  # noqa: F401  (Step 4 에서 사용합니다)


def format_file_list(changed_files):
    """변경 파일 목록을 사람이 읽기 좋은 여러 줄 문자열로 바꾼다.

    입력 예) [{'code': 'M', 'path': 'app.py'}, {'code': '??', 'path': 'a.txt'}]
    출력 예)
        - [M] app.py
        - [??] a.txt
    빈 목록이면 '(변경 파일 없음)' 같은 안내 문자열을 돌려준다.
    """
    # TODO(Step 4): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 4 - prompt_builder.format_file_list()')


def build_commit_prompt(changed_files, diff_text):
    """커밋 메시지 생성을 부탁하는 프롬프트 문자열을 만든다.

    반드시 들어가야 할 것 (테스트가 확인)
        - 변경된 모든 파일 경로
        - diff_text 내용 (diff 가 비어 있어도 오류 없이 동작)
        - 커밋 제목 길이 규칙 숫자 (50자 권장 / 최대 72자)

    넣으면 좋은 것 (교재 Step 4 힌트 참고)
        - 역할: 너는 무엇을 하는 도우미인가
        - 출력 형식: 첫 줄 제목, 빈 줄, 본문 불릿 1~2개
        - 제목 앞머리 규칙: feat / fix / docs / refactor / test ...
        - 출력 언어: 한국어
        - 하지 말 것: 설명 문장, 코드 블록(```) 감싸기
    """
    # TODO(Step 4): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 4 - prompt_builder.build_commit_prompt()')


def build_pr_prompt(changed_files, diff_text, branch_name):
    """PR 제목/본문 초안 생성을 부탁하는 프롬프트 문자열을 만든다.

    반드시 들어가야 할 것 (테스트가 확인)
        - 변경된 모든 파일 경로, diff_text, branch_name
        - 섹션 이름 'Why', 'What', 'How to Test'
        - PR 제목 최대 길이 숫자 (80)

    출력 형식을 정해 두면 받은 뒤 나누기 쉽다. 예)
        첫 줄      : PR 제목 (한 줄)
        그다음 줄부터 : ## Why / ## What / ## How to Test 섹션과 불릿
    """
    # TODO(Step 4): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 4 - prompt_builder.build_pr_prompt()')
