# `ai_gitgen/config.py` — 기본값(상수) 모음

> 상태: ✅ 구현됨 (값은 바꿔도 됨) · 확인: `tests/base/test_03_config.py`

## 1. 모듈의 성격과 역할

프로그램 전체에서 함께 쓰는 규칙 숫자와 기본값을 한 곳에 모은다. 숫자(50, 72, 80 …)가 코드
여기저기에 흩어져 있으면 규칙이 바뀔 때 모두 찾아 고쳐야 하지만, 한 곳에 모으면 한 번만 고치면 된다.
값을 바꾼 뒤에는 `python -m learning_kit.practice base` 로 기본 테스트를 다시 확인한다.

## 2. 포함된 클래스 · 3. 포함된 함수

없음 (상수만 있음).

## 4. 상수의 의미

| 묶음 | 상수 | 값 | 뜻 |
|---|---|---|---|
| API Key | `API_KEY_ENV_NAME` | `'AI_API_KEY'` | 키를 읽어 올 환경변수 **이름** (키 값은 코드에 쓰지 않음) |
| 제공자·모델 | `DEFAULT_PROVIDER` | `'anthropic'` | 기본 AI 제공자. 받은 키의 제공자에 맞춰 고른다 |
| | `DEFAULT_MODEL` | `'claude-haiku-4-5'` | 기본 모델 (아래 "모델별 주의사항") |
| | `PROVIDERS` | 사전 | 제공자별 REST 주소, anthropic 은 `api_version` 도 |
| 파라미터 | `DEFAULT_TEMPERATURE` | `0.3` | 낮을수록 매번 비슷한 결과, 높을수록 다양함 |
| | `TEMPERATURE_MIN` / `MAX` | `0.0` / `1.0` | 두 제공자가 모두 받는 안전한 범위 |
| | `DEFAULT_MAX_TOKENS` | `1024` | 출력 길이 상한 |
| | `MAX_TOKENS_MIN` / `LIMIT` | `1` / `4096` | 비용 폭주를 막는 이 프로그램의 범위 |
| | `REQUEST_TIMEOUT_SECONDS` | `30` | 응답 대기 최대 시간(초) |
| | `MAX_API_CALLS_PER_RUN` | `1` | 1회 실행당 호출 권장 상한 (공식 제약: 1~2회 이내) |
| 출력 규칙 | `COMMIT_TITLE_RECOMMENDED` / `MAX` | `50` / `72` | 커밋 제목 권장 / 최대 길이 |
| | `PR_TITLE_MAX` | `80` | PR 제목 최대 길이 |
| | `PR_SECTIONS` | `('Why', 'What', 'How to Test')` | PR 본문 필수 섹션 |
| 안전 모드 | `SAFE_MODE_MAX_FILES` / `LINES` | `10` / `200` | 전송 제한 (B) 예시 값 |
| 출력 | `SEPARATOR` | `'-' * 40` | 터미널 구분선 |

## 5~6. 누가 사용하나

모든 `ai_gitgen` 모듈과 테스트가 `from ai_gitgen import config` 로 읽는다. 이 모듈은 다른 것을 부르지 않는다.

## 모델별 주의사항 (temperature · max_tokens)

- 공식 미션은 AI 제공자를 정하지 않았다. `PROVIDERS` 에는 많이 쓰는 두 REST 형식을 적어 두었다.
- **anthropic**: `claude-haiku-4-5` 는 저렴한 편이고 API 버전 `2023-06-01` 에서 temperature 를 바꿀 수 있다.
  Claude 4.7 이후 모델은 temperature 를 바꿀 수 없다. Haiku 5.5·Sonnet 5.5 는 기본값 1.0 만 받으므로
  `--temperature 1.0` 으로 실행해야 하고, Opus 계열은 값과 상관없이 temperature 를 거부한다(HTTP 400).
- **openai**: 추론(reasoning) 계열 모델은 temperature 를 바꿀 수 없고 `max_tokens` 대신 `max_completion_tokens` 를 요구한다.
- 실제로 쓸 모델은 제공자 공식 문서에서 지원 여부를 확인한 뒤 `--model` 옵션이나 `DEFAULT_MODEL` 로 바꾼다.

## 7. 기본 / 표준 / 문법 / 프로젝트 구분

| 종류 | 이 모듈에서 |
|---|---|
| 문법/개념 | 상수(대문자 이름), 사전·튜플, 문자열 곱하기 `'-' * 40` |
| 프로젝트 코드 | 모든 상수 |

## 8. 사용한 주요 표준 라이브러리와 이유

없음.
