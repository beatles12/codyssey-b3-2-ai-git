"""출력 형식 검증 및 다듬기 — AI 가 만든 글을 규칙에 맞는지 검사하고 출력한다.

[실습 단계] 🧩 Step 6

[공식 규칙]
    커밋 제목 : 50자 이내 권장 (최대 72자)
    PR 제목   : 최대 80자
    PR 본문   : Why / What / How to Test 섹션 헤더 필수
                + 각 섹션 최소 1개 불릿
    최종 출력 : 구분선/헤더로 구획을 나눠 사용자가 검토하기 쉽게

[왜 검증이 필요할까?]  (공식 체크리스트 항목 4)
    AI 는 부탁한 형식을 가끔 어긴다. 그대로 쓰면 팀 규칙에 맞지 않는
    커밋/PR 이 남는다. 그래서 받은 뒤 프로그램이 한 번 더 확인한다.

[참고] Python 의 len() 은 "글자 수"를 센다. len('가나다') == 3
"""

from ai_gitgen import config  # noqa: F401  (Step 6 에서 사용합니다)


def split_title_body(text):
    """AI 응답 글을 (제목, 본문) 두 부분으로 나눈다.

    규칙
        - 제목 : 비어 있지 않은 첫 줄 (앞뒤 공백 제거)
        - 본문 : 그 아래 나머지 전부 (앞뒤 빈 줄/공백 제거). 없으면 ''.
        - text 가 비어 있으면 ('', '')

    예) 'feat: 검색 추가\\n\\n- search.py 추가'
        -> ('feat: 검색 추가', '- search.py 추가')

    [선택] AI 가 ``` 로 감싸서 답하는 경우도 있다. ``` 줄을 무시하면
    더 튼튼해진다.
    """
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.split_title_body()')


def shorten_title(title, max_length):
    """제목이 max_length 글자보다 길면 max_length 글자 이하로 줄인다.

    - 짧으면 그대로 돌려준다.
    - 줄였다는 표시('...' 또는 '…')를 붙여도 되지만, 붙인 뒤에도
      전체 길이는 max_length 이하여야 한다.
    """
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.shorten_title()')


def validate_commit_message(message, changed_paths=None):
    """커밋 메시지가 규칙을 지키는지 검사해 문제 목록을 돌려준다.

    반환값
        list[str] : 문제 설명 목록. 문제가 없으면 [].

    규칙
        - 제목이 비어 있으면 문제
        - 제목이 config.COMMIT_TITLE_MAX(72)자를 넘으면 문제
          (메시지에 '72' 를 넣어 무엇이 기준인지 알려 준다)
        - 본문이 있는데, 불릿 줄('- ' 또는 '* ' 로 시작)이 하나도 없고
          changed_paths 중 어떤 파일 이름도 언급하지 않으면 문제
          (공식 요약 품질 최소 기준)
    """
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.validate_commit_message()')


def validate_pr_title(title):
    """PR 제목 문제 목록을 돌려준다. (빈 제목, 80자 초과, 여러 줄)"""
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.validate_pr_title()')


def validate_pr_body(body):
    """PR 본문 문제 목록을 돌려준다. 문제가 없으면 [].

    규칙
        - config.PR_SECTIONS 의 각 섹션마다 '#' 으로 시작하는 헤더 줄이
          있어야 한다. 예) '## Why', '### What', '## How to Test'
          (헤더 글자가 섹션 이름으로 "시작"하면 인정: '## Why (변경 배경)')
        - 각 섹션 아래(다음 헤더 전까지)에 불릿 줄이 1개 이상 있어야 한다.
        - 문제 메시지에는 섹션 이름을 넣는다. 예) 'How to Test 섹션이 없습니다'
    """
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.validate_pr_body()')


def format_commit_output(message):
    """커밋 메시지를 구획이 나뉜 터미널 출력용 문자열로 만든다.

    형식 (테스트가 확인)
        --- Commit Message ---     <- 'Commit Message' 가 들어간 헤더 줄
        feat: ...                  <- 헤더 다음의 첫 글자 줄 = 커밋 제목
        (본문)
        ----------------------     <- 구분선 ('-' 3개 이상으로 된 줄)
    """
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.format_commit_output()')


def format_pr_output(title, body):
    """PR 제목과 본문을 구획이 나뉜 터미널 출력용 문자열로 만든다.

    형식 (테스트가 확인)
        --- PR Title ---           <- 'PR Title' 헤더 다음 첫 줄 = 제목
        feat: ...
        --- PR Body ---            <- 'PR Body' 헤더 다음 = 본문
        ## Why
        - ...
        ----------------------     <- 구분선
    """
    # TODO(Step 6): 아래 줄을 지우고 직접 구현하세요.
    raise NotImplementedError('Step 6 - formatter.format_pr_output()')
