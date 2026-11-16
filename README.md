
# AI 커밋 메시지 · PR 초안 생성기 (B3-2)

코디세이 B3-2 「내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기」

## 1. 프로젝트 소개

Git으로 수정한 파일과 변경 내용을 수집하고 AI API를 이용해
커밋 메시지와 Pull Request(PR) 설명 초안을 생성하는 Python CLI 프로그램입니다.

- `commit`: 커밋 메시지 초안 생성
- `pr`: PR 제목과 본문 초안 생성
- `--safe-mode`: 일부 민감정보 마스킹
- `--dry-run`: 실제 AI 호출 없이 전송 내용을 미리 확인

AI가 생성한 글은 초안이므로 사용자가 반드시 검토한 후 적용해야 합니다.

이 프로그램은 Git 커밋, push 또는 GitHub PR을 자동으로 생성하지 않습니다.

## 2. 설치 및 준비

필요 환경:

- Python 3.10 이상
- Git
- AI API Key (실제 AI 사용 시)
- 외부 Python 패키지 설치 불필요

Windows PowerShell 기준:

```powershell
git clone https://github.com/beatles12/codyssey-b3-2-ai-git.git
cd codyssey-b3-2-ai-git
git switch feature/my-b3-2
py --version
git --version
```

현재 제출용 작업 브랜치는 `feature/my-b3-2`입니다.

## 3. AI API 환경변수 설정

기본 연결은 네이토 AI의 Anthropic 호환 API입니다.
요청 주소는 `https://copa.codyssey.kr/v1/messages`이고 기본 모델은
`claude-haiku-4`입니다.

PowerShell에서 발급받은 키를 숨김 입력해 현재 세션의 `AI_API_KEY` 환경변수에 설정합니다.

```powershell
$natoApiKey = Read-Host '네이토 API Key' -AsSecureString
$env:AI_API_KEY = $([System.Net.NetworkCredential]::new('', $natoApiKey).Password)
Remove-Variable natoApiKey
```

키 원문을 코드, README, `.env` 등 어떤 파일에도 저장하거나 Git에 올리지 마세요.
실제 API 호출 시 이용 요금이 발생할 수 있습니다.

## 4. 실행 방법

Git 저장소의 프로젝트 루트에서 실행합니다.

```powershell
py main.py commit
py main.py pr
```

Mac/Linux 또는 `python` 명령이 설정된 환경에서는 다음과 같이 실행할 수 있습니다.

```bash
python main.py commit
python main.py pr
```

안전 모드와 미리보기:

```powershell
py main.py commit --safe-mode --dry-run
py main.py pr --safe-mode --dry-run
```

옵션 조정 예시:

```powershell
py main.py commit --temperature 0.2 --max-tokens 300
py main.py pr --model claude-haiku-4 --max-tokens 600
```

주요 옵션:

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--model` | 사용할 AI 모델 | claude-haiku-4 |
| `--temperature` | 표현 다양성 조절(0.0~1.0) | 0.3 |
| `--max-tokens` | AI 출력 토큰 수 상한(1~4096) | 1024 |
| `--safe-mode` | Git diff의 특정 API Key 패턴과 이메일 마스킹 | 꺼짐 |
| `--dry-run` | AI 호출 없이 프롬프트 미리보기 | 꺼짐 |

## 5. 프로그램 실행 흐름

1. 사용자 명령(commit 또는 pr) 확인
2. Git 저장소 및 변경 파일 확인
3. git status, git diff로 변경 내용 수집
4. 안전 모드 사용 시 일부 민감정보 마스킹
5. 커밋 또는 PR 작성용 프롬프트 생성
6. AI API에 요청 1회 전송
7. AI 응답에서 제목과 본문 추출
8. 길이·형식 검증 후 터미널에 출력

변경사항이 없다면 AI를 호출하지 않고 종료합니다.

## 6. 출력 예시

아래는 가짜 AI를 이용한 모의 실행 결과입니다.

### 커밋 메시지

```text
[INFO] 변경 파일: 3개
[INFO] Git diff: 47줄
[INFO] AI API 호출 횟수: 1
--- Commit Message ---
feat: 할 일 검색 기능 추가

- todo_app/search.py 에 제목 키워드 검색 함수 추가
- README 에 검색 사용 예시 추가
----------------------------------------
```

### PR 제목 및 본문

```text
--- PR Title ---
feat: 할 일 검색 기능 추가
--- PR Body ---
## Why
- 할 일이 많아지면 원하는 항목을 찾기 어려워 검색 기능이 필요했습니다.

## What
- todo_app/search.py 에 키워드 검색 기능을 추가했습니다.
- README에 검색 사용 예시를 추가했습니다.

## How to Test
- 검색 키워드로 검색 기능을 실행해 결과를 확인합니다.
- PR 본문에 필수 섹션과 불릿이 있는지 확인합니다.
----------------------------------------
```

### API Key가 없는 경우

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다. PowerShell에서 환경변수를 설정하세요.
```

### 변경사항이 없는 경우

```text
[INFO] 변경 사항이 없습니다.
```

## 7. AI 파라미터와 출력 형식

### temperature

낮은 값은 상대적으로 일관된 표현을, 높은 값은 다양한 표현을 유도합니다.
단, 일부 모델은 temperature 변경을 지원하지 않을 수 있습니다.

### max_tokens

AI가 생성할 수 있는 출력의 최대 토큰 수를 지정합니다.
값이 너무 작으면 문장이 중간에 끊길 수 있습니다.

### 출력 검증

- 커밋 제목: 50자 권장, 최대 72자
- PR 제목: 최대 80자
- PR 본문: Why / What / How to Test 필수
- 각 PR 섹션: 최소 하나 이상의 불릿 필요

긴 제목은 후처리 방식으로 길이를 제한합니다.
검증 과정에서 발견한 형식 문제는 경고로 안내합니다.

## 8. 민감정보 보호와 비용 관리

`--safe-mode`는 Git diff 텍스트에서 패턴이 맞는 이메일과 `sk-`로 시작하는
키 형태(`sk-` 뒤에 영문자·숫자·`_`·`-`가 16자 이상)를 `[MASKED]`로 바꿉니다.

현재 구현의 제한:

- 전화번호, 일반 비밀번호, 다른 형태의 키는 diff에 남을 수 있습니다.
- 프롬프트에 별도로 포함되는 파일 목록과 PR 브랜치명은 원문을 사용합니다.
- 파일 10개·200줄 전송 제한은 구현하지 않았습니다.
- 스테이징하지 않은 새 파일은 파일 목록에만 표시되며 내용은 diff에 포함되지 않습니다.
- AI가 작성한 내용이 항상 정확하다고 보장할 수 없습니다.

실제 AI를 사용하기 전 `--safe-mode --dry-run`으로
전송할 프롬프트를 확인해야 합니다.

API 호출은 명령 한 번에 최대 1회 수행하도록 구현했습니다.
불필요한 반복 호출을 피하고 변경사항을 작은 단위로 관리합니다.

## 9. 프로젝트 구조

```text
main.py
ai_gitgen/
    cli.py             사용자 명령 및 전체 흐름
    config.py          모델·옵션 기본값
    git_collector.py   Git 변경사항 수집
    safety.py          민감정보 마스킹
    prompt_builder.py  AI 프롬프트 작성
    ai_client.py       AI API 통신 및 오류 처리
    formatter.py       출력 형식 검증
learning_kit/          학습용 가짜 AI·시연 도구
tests/                 자동 테스트
docs/                  설계·학습 문서
```

Git 수집 기능과 AI API 호출 기능을 분리해
각 기능을 독립적으로 테스트하고 오류 원인을 찾기 쉽게 설계했습니다.

프롬프트 작성과 결과 검증 기능도 분리했습니다.
AI가 지시를 따르지 않더라도 결과를 다시 검사하기 위해서입니다.

## 10. 테스트 방법

PowerShell에서 실행합니다.

```powershell
py -m learning_kit.practice base
py -m learning_kit.practice 7
py -m learning_kit.practice 8
py -m learning_kit.demo 7
```

자동 테스트와 시연은 가짜 AI를 사용하므로
실제 API 호출 비용이 발생하지 않습니다.

실제 네이토 API 연동에서도 커밋 메시지와 PR 초안 생성을 확인했습니다.

## 11. 학습 및 설계 자료

- `START_HERE.md`: 실습 시작 안내
- `docs/PRACTICE_STEPS.md`: 단계별 실습
- `docs/B3-2_STUDY_GUIDE.html`: 시각화 학습 자료
- `docs/architecture.md`: 프로그램 구조 설명
- `docs/modules/`: 모듈별 함수·역할 설명
- `docs/REQUIREMENTS_ANALYSIS.md`: 요구사항 분석
