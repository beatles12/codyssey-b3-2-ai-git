"""ai_gitgen — Git 변경 사항으로 커밋 메시지/PR 초안을 만드는 CLI 도구.

모듈 한눈에 보기 (실습 단계 순서)
    config.py          ✅ 구현됨   기본값(상수) 모음
    cli.py             🧩 Step 1   명령줄 옵션 만들기, 입력값 검사
    git_collector.py   🧩 Step 2   git status / git diff 결과 수집
    safety.py          🧩 Step 3   민감정보 마스킹, 전송량 제한 (--safe-mode)
    prompt_builder.py  🧩 Step 4   AI 에게 보낼 요청문(프롬프트) 만들기
    ai_client.py       🧩 Step 5   AI API 요청/응답/오류 처리
    formatter.py       🧩 Step 6   길이·형식 검증과 출력 다듬기
    cli.py             🧩 Step 7   전체 흐름 연결 (commit / pr 명령)

🧩 표시가 붙은 함수는 `raise NotImplementedError(...)` 로 비어 있습니다.
직접 구현하면서 `python -m learning_kit.practice <단계번호>` 로 확인하세요.
"""

__version__ = '0.1.0'
