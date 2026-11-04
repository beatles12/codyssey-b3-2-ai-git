# practice_data — 연습용 데이터

실제 AI API 를 부르지 않고도 각 단계를 연습할 수 있도록 준비한 데이터입니다.
**모든 키·이메일·전화번호는 가짜 값입니다.** (실제 비밀키는 이 저장소 어디에도 없습니다.)

| 파일 | 내용 | 쓰는 단계 |
|---|---|---|
| `git_status_sample.txt` | `git status --porcelain` 출력 예. 상태 코드 7종(` M`, `M `, `A `, `MM`, `D `, `R `, `??`) | Step 2 |
| `git_diff_sample.diff` | 연습 저장소 `feature` 시나리오의 실제 `git diff --cached` + `git diff` 출력 | Step 2, 4 |
| `git_diff_with_secrets.diff` | 가짜 API Key·이메일·전화번호·비밀번호가 들어간 diff | Step 3 |
| `git_log_sample.txt` | `git log` 출력 예 — diff 와 무엇이 다른지 비교용 | 교재 |
| `api_responses/anthropic_commit.json` | Anthropic 응답 모양 (맨 앞에 `thinking` 블록 있음 주의) | Step 5 |
| `api_responses/anthropic_pr.json` | PR 초안 응답 모양 | Step 5, 6 |
| `api_responses/anthropic_max_tokens.json` | `stop_reason` 이 `max_tokens` 인 응답 (출력이 잘린 경우) | Step 5 |
| `api_responses/openai_commit.json` | OpenAI 호환 응답 모양 (`choices[0].message.content`) | Step 5 |
| `api_responses/anthropic_error_401.json` | 인증 실패(잘못된 키) 오류 본문 | Step 5 |
| `api_responses/anthropic_error_400.json` | 잘못된 요청 오류 본문 (메시지 문구는 예시) | Step 5 |
| `api_responses/anthropic_error_429.json` | 요청 과다 오류 본문 (메시지 문구는 예시) | Step 5 |
| `expected_outputs/*.txt` | 최종 터미널 출력 참고 예시 (정답 아님) | Step 6, 7 |

> `api_responses/` 의 응답은 `learning_kit/fake_ai.py` 로 만든 **모양 예시**입니다.
> 실제 제공자 응답에는 필드가 더 있을 수 있고, 오류 메시지 문구도 다를 수 있습니다.
> 실제 형식은 제공자 공식 문서에서 확인하세요.

## 진짜 Git 저장소로 연습하기

파일이 아니라 진짜 Git 저장소에서 연습하려면:

```bash
python -m learning_kit.practice_repo --list      # 시나리오 목록
python -m learning_kit.practice_repo feature     # practice_repo/ 폴더 생성
```

`practice_repo/` 는 `.gitignore` 에 등록되어 있어 이 프로젝트에 커밋되지 않습니다.
