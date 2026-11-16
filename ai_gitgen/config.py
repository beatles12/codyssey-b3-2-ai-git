"""프로그램 전체에서 쓰는 기본값(상수). 의미와 모델별 주의사항: docs/modules/config.md"""

# 1. API Key 를 읽어 올 환경변수 이름 (키 "값"은 코드에 쓰지 않는다)
API_KEY_ENV_NAME = 'AI_API_KEY'

# 2. AI 제공자와 모델 기본값 (받은 키의 제공자에 맞춰 고른다)
DEFAULT_PROVIDER = 'anthropic'
DEFAULT_MODEL = 'claude-haiku-4'
PROVIDERS = {
    'anthropic': {'url': 'https://copa.codyssey.kr/v1/messages',
                  'api_version': '2023-06-01'},
    'openai': {'url': 'https://api.openai.com/v1/chat/completions'},
}

# 3. API 호출 파라미터 기본값과 허용 범위 (CLI 옵션의 기본값)
DEFAULT_TEMPERATURE = 0.3      # 낮을수록 일관된 결과, 높을수록 다양함
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0          # 두 제공자가 모두 받는 범위
DEFAULT_MAX_TOKENS = 1024      # 출력 길이 상한
MAX_TOKENS_MIN = 1
MAX_TOKENS_LIMIT = 4096        # 비용 폭주를 막는 상한
REQUEST_TIMEOUT_SECONDS = 30   # 응답 대기 최대 시간(초)
MAX_API_CALLS_PER_RUN = 1      # 공식 제약: 1회 실행당 1~2회 이내

# 4. 출력 형식 규칙 (공식 요구사항 '출력 형식 검증 및 다듬기')
COMMIT_TITLE_RECOMMENDED = 50
COMMIT_TITLE_MAX = 72
PR_TITLE_MAX = 80
PR_SECTIONS = ('Why', 'What', 'How to Test')

# 5. 안전 모드 전송 제한 (공식 제약 (B) 예시 값)
SAFE_MODE_MAX_FILES = 10
SAFE_MODE_MAX_LINES = 200

# 6. 터미널 출력 구분선
SEPARATOR = '-' * 40
