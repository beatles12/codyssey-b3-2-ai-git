# START HERE — B3-2 실습을 혼자 시작하는 방법

이 저장소는 코디세이 **B3-2 「내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기」** 를
**직접 구현하면서 원리를 이해하기 위한 실습 환경**입니다.

- ✅ 준비된 것: 폴더 구조, 함수 이름과 한 줄 설명, 함수별 명세 문서(`docs/modules/`), 연습 데이터, 가짜 AI, 자동 테스트, 교재
- 🧩 직접 할 것: `ai_gitgen/` 안의 **TODO 함수 본문** (미션 완성 코드는 들어 있지 않습니다)
- 🔒 실제 AI API 는 **Step 8 에서 한두 번만** 씁니다. 그 전까지는 키 없이, 비용 없이 연습합니다.

---

## 1. 처음 10분 — 이것만 따라 하세요

```bash
# 1) 저장소 폴더로 이동 (이 파일이 있는 폴더)
cd codyssey-b3-2-ai-git

# 2) 내 작업 브랜치 만들기 (main 에서 바로 작업하지 않기)
git switch -c feature/my-b3-2

# 3) 실습 환경 점검 — 마지막에 "★ 실습 환경이 준비되었습니다" 가 나오면 성공
python -m learning_kit.check_env

# 4) 전체 진행 현황 보기 — 지금은 모두 TODO
python -m learning_kit.practice
```

> Mac/Linux 에서 `python` 이 없다고 나오면 `python3` 로, Windows 에서는 `py` 로 바꿔 실행하세요.

그다음 브라우저로 **[`docs/B3-2_STUDY_GUIDE.html`](docs/B3-2_STUDY_GUIDE.html)** 을 엽니다. (파일을 더블클릭, 인터넷 불필요)

---

## 2. 지금 저장소 상태

| 구분 | 파일 | 상태 |
|---|---|---|
| 실행 파일 | `main.py` | ✅ 구현됨 (TODO 가 남아 있으면 `[TODO]` 안내만 출력) |
| 기본값 | `ai_gitgen/config.py` | ✅ 구현됨 (값은 바꿔도 됨) |
| Step 1, 7 | `ai_gitgen/cli.py` | 🧩 TODO (출력 함수 `log()` 만 구현됨) |
| Step 2 | `ai_gitgen/git_collector.py` | 🧩 TODO |
| Step 3 | `ai_gitgen/safety.py` | 🧩 TODO |
| Step 4 | `ai_gitgen/prompt_builder.py` | 🧩 TODO |
| Step 5 | `ai_gitgen/ai_client.py` | 🧩 TODO (예외 클래스만 구현됨) |
| Step 6 | `ai_gitgen/formatter.py` | 🧩 TODO |
| Step 8 | `README.md` | 🧩 TODO (지금은 안내문) |
| 학습 도구 | `learning_kit/` | ✅ 구현됨 — 미션 제출 범위 아님 |
| 연습 데이터 | `practice_data/` | ✅ 준비됨 (모든 키·이메일은 가짜) |
| 기본 테스트 | `tests/base/` | ✅ **지금 모두 통과** |
| 연습 테스트 | `tests/practice/` | 🧩 구현 전에는 `[TODO]` (Step 1~8) |

---

## 3. 권장 학습 순서

| 순서 | 할 일 | 자료 | 시간 |
|---|---|---|---|
| ① | 환경 점검 (위 1절) | `python -m learning_kit.check_env` | 10분 |
| ② | 미션이 무엇인지 이해 | 교재 1~2절 (미션 한눈에, 프로그램 구조도) | 30분 |
| ③ | Git 과 API 기본 개념 | 교재 3~5절 (diff vs log, AI 에 전달하는 원리, API 와 환경변수) | 1시간 |
| ④ | 흐름 그림 익히기 | 교재 6~9절 (커밋·PR 생성 흐름, 함수 호출 흐름도, 함수 종류 구분) | 40분 |
| ⑤ | **Step 1 → 8 실습** | [`docs/PRACTICE_STEPS.md`](docs/PRACTICE_STEPS.md) + 교재 10절 | 약 30~40시간 |
| ⑥ | 설명 연습 | [`docs/templates/MY_ANSWERS.md`](docs/templates/MY_ANSWERS.md), 교재 '30초 설명' | 2시간 |
| ⑦ | (선택) 보너스 | [`docs/REQUIREMENTS_ANALYSIS.md`](docs/REQUIREMENTS_ANALYSIS.md) 2-3절 | — |

### 각 Step 에서 반복하는 5단계

```text
1. 읽기   : 교재/워크북의 Step N  (무엇을, 왜, 힌트) + docs/modules/<모듈>.md (함수 명세)
2. 구현   : 해당 파일의 TODO 함수 본문 작성 (raise NotImplementedError 줄 지우기)
3. 눈으로 : python -m learning_kit.demo N
4. 채점   : python -m learning_kit.practice N        (-v 를 붙이면 자세히)
5. 저장   : git add <파일> && git commit -m "feat: ..."
```

---

## 4. 자주 쓰는 명령

| 명령 | 하는 일 |
|---|---|
| `python -m learning_kit.check_env` | 환경 점검 + 기본 테스트 |
| `python -m learning_kit.practice` | 전체 진행 현황표 (다음 할 단계 안내) |
| `python -m learning_kit.practice 3` | Step 3 연습 테스트 자세히 |
| `python -m learning_kit.practice 3 -v` | 실패 원인(Traceback)까지 |
| `python -m learning_kit.practice base` | 기본 테스트만 |
| `python -m learning_kit.demo 3` | Step 3 함수 결과를 눈으로 보기 (가짜 AI) |
| `python -m learning_kit.practice_repo --list` | 연습용 Git 저장소 시나리오 목록 |
| `python -m learning_kit.practice_repo secret` | `practice_repo/` 에 연습 저장소 만들기 |
| `python -m unittest discover -s tests/base -t .` | 표준 방식으로 기본 테스트 실행 |

결과 읽는 법: `[통과]` 조건 만족 · `[TODO]` 아직 구현 전 · `[실패]` 결과가 기대와 다름 · `[오류]` 예상 못 한 예외 · `(선택)` 미션 필수 아님

---

## 5. 폴더 지도

```text
codyssey-b3-2-ai-git/
├── START_HERE.md            ← 지금 읽는 파일
├── README.md                ← Step 8 에서 제출용으로 다시 작성
├── CODYSSEY_CODING_GUIDELINES.md  코디세이 공통 코딩 기준
├── main.py                  ✅ 실행 파일: python main.py commit / pr
├── ai_gitgen/               🧩 미션 코드 (내가 구현)
│   ├── config.py            ✅ 기본값 (50/72/80자, 10파일/200줄, 모델 …)
│   ├── cli.py               🧩 Step 1, 7
│   ├── git_collector.py     🧩 Step 2
│   ├── safety.py            🧩 Step 3
│   ├── prompt_builder.py    🧩 Step 4
│   ├── ai_client.py         🧩 Step 5
│   └── formatter.py         🧩 Step 6
├── learning_kit/            ✅ 학습 도구 (가짜 AI, 테스트 러너, 데모, 연습 저장소)
├── practice_data/           ✅ 연습용 git status / diff / log / API 응답 (모두 가짜 값)
├── tests/
│   ├── base/                ✅ 기본 환경 테스트 (지금 통과)
│   └── practice/            🧩 Step 1~8 연습 테스트
└── docs/
    ├── B3-2_STUDY_GUIDE.html   교재 (오프라인)
    ├── PRACTICE_STEPS.md       단계별 워크북
    ├── REQUIREMENTS_ANALYSIS.md 공식 요구사항 분석 · 가이드라인 적용
    ├── architecture.md         구조 · 데이터 흐름 · 설계 이유 · 한계
    ├── modules/                모듈별 문서 (함수 입력·출력·호출 관계 = 명세)
    └── templates/              README 작성 틀, 설명 답안 노트
```

---

## 6. 꼭 지킬 안전 규칙

1. **API Key 는 터미널 환경변수로만.** 코드·README·커밋 메시지·스크린샷에 넣지 않습니다.
   (`tests/base/test_05_security.py` 가 키처럼 보이는 문자열을 계속 감시합니다.)
2. **실제 AI API 는 Step 8 에서만**, 그것도 `--dry-run` 으로 보낼 내용을 먼저 본 뒤 1~2회.
3. 테스트와 데모는 실제 네트워크 호출을 **자동으로 막습니다.** 막혔다는 오류가 나면 `transport` 를 끝까지 넘겼는지 보세요.
4. `main` 브랜치에서 바로 작업하지 않고 **작업 브랜치**에서 커밋합니다.
5. 키를 실수로 커밋했다면 **즉시 제공자 사이트에서 키를 폐기(재발급)** 하세요. 커밋을 지워도 기록에 남을 수 있습니다.

---

## 7. 문제가 생겼을 때

| 증상 | 해결 |
|---|---|
| `No module named learning_kit` / `ai_gitgen` | 저장소 루트에서 실행했는지 확인 (`ls` 했을 때 `main.py` 가 보여야 함) |
| `python: command not found` | `python3` (Mac/Linux) 또는 `py` (Windows) |
| 기본 테스트가 실패 | `python -m learning_kit.practice base -v` 로 원인 확인. 함수 이름·매개변수 이름을 바꾸지 않았는지 |
| 연습 테스트가 `[오류]` | `-v` 로 Traceback 의 **마지막 줄**과 **내 파일의 줄 번호** 확인 |
| `RuntimeError: ... 네트워크 ... 금지` | 실제 통신을 하려 함 → `transport` 를 넘겼는지 |
| 한글이 깨짐 (Windows) | `subprocess.run(..., encoding='utf-8')`, 터미널은 Windows Terminal 권장 |
| 연습 저장소가 꼬임 | `python -m learning_kit.practice_repo feature` 로 다시 만들기 (기존 연습 저장소만 지움) |

---

## 8. 알아 둘 점 (준비 과정에서 확인된 사항)

- **코딩 가이드라인**: 저장소 루트의 `CODYSSEY_CODING_GUIDELINES.md` 를 따릅니다. 함수 위에는 한 줄 설명만 두고, 상세 명세는 `docs/modules/` 에 둡니다. 공통 예외는 `main()` 에 붙인 데코레이터 한 곳에서 처리합니다. (`docs/REQUIREMENTS_ANALYSIS.md` 7절)
- **AI 제공자 미정**: 공식 미션은 제공자를 정하지 않습니다. `config.py` 에 anthropic / openai 두 형식을 준비했습니다. 필수 테스트는 `config.DEFAULT_PROVIDER` 에 고른 형식 하나만 확인하고, 다른 형식은 (선택) 테스트입니다.
- **temperature 지원 여부**: 최신 모델 중에는 temperature 를 거부(HTTP 400)하는 모델이 있습니다. 기본 모델은 temperature 를 받는 모델로 두었습니다. OpenAI 추론 계열 모델은 `max_tokens` 대신 `max_completion_tokens` 를 요구합니다. 실제 사용 전 제공자 문서를 꼭 확인하세요.
- **필수와 선택**: `(선택)` 이 붙은 테스트는 공식 미션 필수가 아닙니다. 예: safe-mode 의 전송 제한(B), 다른 제공자 형식, `--dry-run`.
- 공식 문서와 이 실습 자료가 다르면 **공식 문서가 우선**입니다.
