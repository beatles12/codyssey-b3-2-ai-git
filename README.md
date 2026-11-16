# AI 커밋 메시지 · PR 초안 생성기 (B3-2)

코디세이 B3-2 「내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기」

## 목차

- [프로그램 소개](#프로그램-소개)
- [설치와 오프라인 첫 시연](#설치와-오프라인-첫-시연)
- [전체 처리 흐름과 코드 위치](#전체-처리-흐름과-코드-위치)
- [변경 수집과 프롬프트 미리보기](#변경-수집과-프롬프트-미리보기)
- [AI 요청과 옵션 비교](#ai-요청과-옵션-비교)
- [출력 형식과 검토](#출력-형식과-검토)
- [변경 없음과 오류 처리](#변경-없음과-오류-처리)
- [민감정보와 안전 모드](#민감정보와-안전-모드)
- [실제 API 사용과 키 입력](#실제-api-사용과-키-입력)
- [팀에서 먼저 개선할 기능](#팀에서-먼저-개선할-기능)
- [자동 테스트와 참고 자료](#자동-테스트와-참고-자료)

## 프로그램 소개

수정한 파일과 변경 내용을 근거로 커밋 메시지와 PR 설명의 **초안**을 만드는 Python 프로그램입니다. 예를 들어 팀의 할 일 관리 프로그램에 검색 기능을 추가했다면, 작업자는 변경 기록과 동료에게 보낼 검토 요청서를 준비하는 시간을 줄일 수 있습니다.

- **Git**은 파일 변경 이력을 관리하는 도구입니다. 사무실에서 문서의 수정본과 변경 이력을 모아 두는 장부에 해당합니다.
- **커밋**은 작업의 한 시점을 기록하는 단위입니다. 커밋 메시지는 장부에 붙이는 변경 요약입니다. `commit` 명령으로 그 문구를 작성합니다.
- **PR(Pull Request)**은 변경 내용을 동료에게 검토해 달라고 요청하는 절차입니다. `pr` 명령으로 검토 요청서에 쓸 제목과 본문을 작성합니다.
- **CLI**는 PowerShell 같은 창에서 글자로 조작하는 방식입니다. `py main.py pr`은 접수 창구에 “PR 초안을 만들어 주세요”라고 전달하는 명령입니다.

프로그램의 결과는 터미널에 표시됩니다. 커밋 생성, GitHub 업로드, PR 등록은 초안을 검토한 사람이 직접 진행합니다.

## 설치와 오프라인 첫 시연

Python 3.10 이상, Git, PowerShell을 사용합니다. Python의 기본 도구만 사용하므로 외부 패키지 설치는 필요하지 않습니다. 처음 내려받을 때는 다음 순서로 준비합니다.

```powershell
git clone https://github.com/beatles12/codyssey-b3-2-ai-git.git
cd codyssey-b3-2-ai-git
git switch feature/my-b3-2
py --version
git --version
```

이미 내려받았다면 VS Code에서 `main.py`가 있는 프로젝트 폴더를 열고 **터미널 → 새 터미널**을 선택합니다. 아래 예시는 Windows의 `py` 명령을 사용합니다. Python이 설치되어 있고 `python --version`이 동작하는 환경이라면 `py` 대신 `python`을 쓰면 됩니다.

**화면을 보여주는 순서**는 VS Code에서 `main.py`의 `run()`을 열고, PowerShell에서 도움말과 모의 시연을 실행하는 것입니다.

```powershell
py main.py --help
py main.py pr --help
py -m learning_kit.demo 7
```

`demo 7`은 연습용 Git 저장소를 임시 폴더에 만들고 시험용 응답을 돌려주는 `FakeTransport`를 연결합니다. 샘플 견적서로 결재 절차를 연습하듯, 키나 네트워크 없이 커밋 초안, PR 초안, 변경 없음, 키 누락, 안전 모드를 차례로 보여줍니다. 출력의 `AI API 호출 횟수: 1`은 이 시연에서는 **가짜 통신 함수가 한 번 실행됐다는 뜻**입니다. [전체 시연 코드](learning_kit/demo.py#L241) · [가짜 통신 코드](learning_kit/fake_ai.py#L98)

## 전체 처리 흐름과 코드 위치

변경 기록을 찾아 요청서를 만들고, 외부 작성 담당에게 보낸 뒤 돌아온 초안을 검토하는 순서입니다. 아래 그림은 변경사항이 있는 일반 실행 경로입니다.

```text
main.py → cli.py → Git 변경 수집 → 프롬프트 작성 → AI API → 출력 검증 → PowerShell에 표시
                       ↓              ↓
                safe-mode 마스킹   dry-run은 여기에서 미리보기 후 종료
```

**함수**는 이름이 붙은 작업 절차입니다. VS Code에서 아래 파일을 열고 `Ctrl+F`로 함수 이름을 찾으면 각 담당자가 다음 사람에게 어떤 자료를 넘기는지 따라갈 수 있습니다.

| 코드 위치 | 담당 업무와 사무실 비유 | 누가 호출하고 다음에 무엇을 하는가 |
| --- | --- | --- |
| [main.py](main.py#L23) | 접수 번호표 발급. 프로그램을 시작하고 종료 상태를 PowerShell에 전달합니다. | PowerShell에서 스크립트를 실행하면 `run()`이 `cli.main()`을 호출합니다. |
| [cli.py](ai_gitgen/cli.py#L195) | 업무 배정 담당. 명령과 선택 사항을 읽고 처리 순서를 정합니다. | `main()`은 `build_parser()`와 `validate_options()`를 거쳐 `run_commit()` 또는 `run_pr()`을 실행합니다. 두 함수는 `collect_changes()` → 프롬프트 작성 → `request_ai()` → 출력 정리 순으로 진행합니다. |
| [git_collector.py](ai_gitgen/git_collector.py#L60) | 변경 장부 열람 담당. 어떤 파일의 어떤 줄이 달라졌는지 가져옵니다. | `cli.collect_changes()`가 `is_git_repository()`, `get_changed_files()`, `get_diff()`를 호출합니다. 수집 함수는 `run_git()`으로 Git을 실행하고, 파일 목록은 `parse_status_output()`으로 정리합니다. `cli.run_pr()`은 `get_current_branch()`로 현재 작업 분기의 이름도 가져옵니다. |
| [safety.py](ai_gitgen/safety.py#L16) | 발송 자료의 일부에 가림 표시를 하는 담당입니다. | `cli.collect_changes()`가 `--safe-mode`에서 `apply_safe_mode()`를 호출합니다. 이 함수는 `mask_sensitive()`가 가린 diff를 돌려줍니다. |
| [prompt_builder.py](ai_gitgen/prompt_builder.py#L18) | 작성 의뢰서 담당. 참고 자료와 결과물에 필요한 형식을 묶습니다. | `cli.run_commit()`과 `cli.run_pr()`이 각각 `build_commit_prompt()`, `build_pr_prompt()`를 호출합니다. 두 함수는 `format_file_list()`로 파일 목록을 적고 완성된 프롬프트를 돌려줍니다. |
| [ai_client.py](ai_gitgen/ai_client.py#L151) | 발송·수신 담당. 의뢰서를 보내고 회신에서 초안 부분을 꺼냅니다. | `cli.request_ai()`가 `call_ai_api()`를 호출합니다. 이 함수는 `get_api_key()`, `build_headers()`, `build_request_body()`를 사용한 뒤 `send_http_request()` 또는 시연용 통신 함수를 실행하고 `extract_text()`로 응답의 글을 꺼냅니다. |
| [formatter.py](ai_gitgen/formatter.py#L11) | 편집 담당. 원고의 제목을 찾고 출력 양식을 점검합니다. | `cli.run_commit()`은 `split_title_body()`, `run_pr()`은 `split_pr_title_body()`를 호출합니다. 두 경로 모두 `shorten_title()`을 거쳐 각각 커밋 또는 PR 검증 함수로 넘어갑니다. 마지막으로 `format_commit_output()` 또는 `format_pr_output()`이 표시할 문자열을 만듭니다. |
| [config.py](ai_gitgen/config.py#L3) | 공용 업무 기준표. 기본 모델, 글자 수, 옵션 범위를 한곳에 둡니다. | CLI, 요청 작성, 검증 함수가 값을 읽습니다. `config.py`는 설정을 제공하는 모듈로, 다른 작업 함수를 호출하지 않습니다. |

**Git 수집과 AI 통신을 분리한 이유**는 자료를 모으는 일과 외부 서비스로 보내는 일의 실패 원인이 다르기 때문입니다. 저장소 경로나 Git 명령이 문제라면 `git_collector.py`를, 연결이나 인증 문제라면 `ai_client.py`를 확인할 수 있습니다. 자료 수집만 로컬에서 시험하거나, 실제 발송 자리에 모의 통신을 연결하기도 쉽습니다.

**프롬프트 작성과 출력 포맷팅을 분리한 이유**는 요청서에 적은 규칙과 돌아온 답변의 실제 형식이 다를 수 있기 때문입니다. `prompt_builder.py`로 의뢰 내용을 바꾸더라도 `formatter.py`에서 기존 응답 예시를 사용해 제목 분리와 형식 검사를 독립적으로 확인할 수 있습니다.

## 변경 수집과 프롬프트 미리보기

`git status`는 **수정한 파일의 목록**, `git diff`는 **어느 줄을 지우고 더했는지 표시한 수정 대비표**입니다. 결재에 올리기로 표시한 변경을 **스테이징된 변경**이라고 합니다. `get_diff()`는 `git diff --cached`로 표시한 변경과 `git diff`로 아직 표시하지 않은 변경을 모읍니다. 스테이징하지 않은 새 파일은 이름이 목록에 들어가며, 파일 본문은 diff에 포함되지 않습니다. [Git 수집 코드](ai_gitgen/git_collector.py#L60)

**프롬프트**는 AI에 전달하는 작업 지시서입니다. `build_commit_prompt()`는 파일 목록과 diff를 붙여 한국어 한 줄 제목과 필요할 때만 쓰는 변경 요약을 요청합니다. 커밋 기록을 빠르게 훑기 위한 구성입니다. `build_pr_prompt()`는 같은 자료에 현재 브랜치(작업 분기)를 더하고, 동료가 배경·변경점·확인 방법을 읽을 수 있도록 섹션과 불릿을 요청합니다. 자료에 없는 변경이나 확인하지 않은 테스트를 사실처럼 쓰지 않도록 지시합니다. [프롬프트 작성 함수](ai_gitgen/prompt_builder.py#L18)

**PowerShell 시연**은 프로젝트 폴더에서 시작합니다. 첫 줄에서 프로그램 위치를 기억해 두므로 다른 저장소로 이동한 뒤에도 같은 `main.py`를 실행할 수 있습니다. `feature`는 볼 수 있는 변경이 들어 있는 연습용 저장소입니다.

```powershell
$app = (Resolve-Path .\main.py).Path
$demoDir = Join-Path ([System.IO.Path]::GetTempPath()) ('b3-2-demo-' + [guid]::NewGuid().ToString('N'))
py -m learning_kit.practice_repo feature --path (Join-Path $demoDir 'feature')
Push-Location (Join-Path $demoDir 'feature')
git status --short
git diff --cached
git diff
py $app commit --safe-mode --dry-run
py $app pr --safe-mode --dry-run
Pop-Location
```

화면에서 파일 목록과 diff를 먼저 보여주고, 두 프롬프트의 요청 내용이 어떻게 다른지 비교합니다. `--dry-run`은 발송 전 미리보기와 같아 요청서를 화면에만 표시합니다. `Pop-Location`을 실행하면 프로그램이 있는 폴더로 돌아옵니다.

## AI 요청과 옵션 비교

**AI API**는 다른 프로그램이 AI 서비스에 작업을 부탁할 때 쓰는 접수 창구입니다. `build_headers()`가 발신자 확인용 정보와 요청 형식을 준비하고, `build_request_body()`가 지시서와 옵션을 요청 본문에 담습니다. 그 본문은 **JSON**, 즉 항목 이름과 값을 짝지어 적는 전자 양식으로 전달됩니다. `extract_text()`는 회신 양식에서 생성된 글을 꺼냅니다. PowerShell에서 `py -m learning_kit.demo 5`를 실행하면 실제 키 없이 요청 주소, 가짜 요청 본문, 모의 회신을 볼 수 있습니다. [AI 요청 작성 코드](ai_gitgen/ai_client.py#L20)

`temperature`와 `max_tokens`를 CLI 옵션으로 두면 문서 작성자가 실행할 때마다 요청 조건을 정할 수 있습니다. `build_parser()`가 값을 읽고 `validate_options()`가 범위를 검사한 뒤, `request_ai()`를 거쳐 요청 본문으로 전달합니다. PowerShell의 `--max-tokens`는 요청 본문에서 `max_tokens`라는 항목에 들어갑니다. [옵션 처리 코드](ai_gitgen/cli.py#L18)

| CLI 옵션 | 뜻과 업무 비유 | 기본값 |
| --- | --- | --- |
| `--model` | 초안을 작성할 AI 모델을 고릅니다. | `claude-haiku-4` |
| `--temperature` | 표현 선택의 폭을 조절합니다. 같은 업무 메모를 익숙한 문구로 쓰거나 다른 표현도 시도해 보는 차이입니다. 값이 낮으면 표현이 비교적 일정한 경향이 있고, 높으면 다양해질 수 있습니다. 허용 범위는 `0.0~1.0`입니다. | `0.3` |
| `--max-tokens` | 생성할 답변의 최대 분량을 정합니다. 보고서에 사용할 분량 한도와 같습니다. 토큰은 AI가 읽고 쓰는 글의 조각으로, 글자 수와 일치하지 않습니다. 너무 낮으면 답변이 중간에서 끊길 수 있습니다. 허용 범위는 `1~4096`입니다. | `1024` |
| `--safe-mode` | 발송 자료인 diff에서 지정한 민감정보 패턴을 가립니다. | 꺼짐 |
| `--dry-run` | 작성 의뢰서를 화면에서 미리 봅니다. | 꺼짐 |

`--max-tokens`를 생략하면 요청에 출력 상한 `1024`가 들어갑니다. 이 기본값을 처음 정한 근거는 프로젝트 자료에서 확인되지 않습니다. 값을 조정할 때는 답변이 중간에 끊기는지, PR의 필수 섹션과 불릿이 끝까지 완성되는지, 실제 사용량에 따른 비용이 적절한지 함께 확인합니다. 답변이 잘리면 상한을 높여 보고, 더 낮은 상한에서도 필요한 내용이 완성되면 그 값을 사용합니다.

**토큰 사용 없는 비교 실습**입니다. 위에서부터 첫 번째와 두 번째는 표현 옵션만, 첫 번째와 세 번째는 분량 옵션만 바꿉니다.

```powershell
py -m learning_kit.demo 7 --temperature 0.2 --max-tokens 300
py -m learning_kit.demo 7 --temperature 0.8 --max-tokens 300
py -m learning_kit.demo 7 --temperature 0.2 --max-tokens 700
py -m unittest tests.practice.test_step7_flow.CommitFlowTest.test_cli_options_reach_request
```

모의 시연의 `명령=…`에서 어떤 옵션이 주어졌는지 확인하고, 마지막 테스트로 옵션이 가짜 AI에게 전달된 요청 본문에도 들어가는지 확인합니다. 모의 답변은 정해진 예시이므로 동일하게 출력됩니다. **옵션 변경에 따른 실제 AI 답변 차이는 별도 검증이 필요합니다.** 실제 서비스를 사용해 비교하는 경우에는 같은 브랜치·diff·모델·명령에서 한 값씩 바꾸고, 표현의 차이, 답변 분량, 필수 섹션의 완성 여부를 관찰합니다. 모델이 값을 지원하더라도 매번 다른 표현이나 정해진 길이의 답변을 보장하지는 않습니다.

## 출력 형식과 검토

초안을 받으면 편집자가 제목과 본문을 분리하고 규격을 확인하듯 포매터가 형식을 점검합니다. `split_title_body()`는 커밋 응답을 나누고, `split_pr_title_body()`는 `# PR 제목` 같은 표지 다음에 실제 제목이 있으면 그 제목을 가져옵니다. 응답 전체를 감싼 코드블록 표시는 걷어 내고, 본문 속 코드 예시는 그대로 둡니다. [출력 정리 함수](ai_gitgen/formatter.py#L11)

| 출력 | 확인하는 기준 | 이유 |
| --- | --- | --- |
| 커밋 메시지 | 한 줄 제목. 50자 이내 권장, 최대 72자. 본문을 쓰면 불릿 또는 변경 파일 설명을 포함합니다. | 변경 장부에서 핵심을 빠르게 찾기 쉽습니다. |
| PR 제목 | 한 줄, 최대 80자. | 검토 목록에서 무슨 변경인지 파악하기 쉽습니다. |
| PR 본문 | **Why**(왜 바꿨는가), **What**(무엇을 바꿨는가), **How to Test**(어떻게 확인하는가). 각 섹션에 `- `나 `* `로 시작하는 불릿(목록 항목)이 최소 하나 필요합니다. | 검토자가 배경과 결과를 이해하고 확인 절차를 따라갈 수 있습니다. |

**재생성**은 규칙을 어긴 초안을 AI에 돌려보내 다시 써 달라고 하는 방식입니다. 빠진 설명을 보완할 기회가 생기는 대신 요청 시간과 토큰 사용이 늘고, 형식이 바로잡힐지는 응답에 달려 있습니다. **후처리**는 받은 초안을 프로그램에서 정리하는 방식입니다. 현재는 이 방식을 선택해 실제 요청 경로에서 한 번만 호출합니다. `shorten_title()`은 최대 글자 수에 맞춰 제목을 줄이고, `validate_commit_message()`, `validate_pr_title()`, `validate_pr_body()`는 남은 형식 문제를 경고합니다. 누락된 테스트 절차는 사용자가 확인해서 채웁니다.

`py -m learning_kit.demo 6`을 실행하면 긴 제목을 줄인 결과와 섹션이 빠진 모의 PR의 검증 결과를 볼 수 있습니다. `demo 7`에서는 아래와 같은 결과를 실제 CLI의 출력 구획으로 확인할 수 있습니다.

```text
--- Commit Message ---
feat: 할 일 검색 기능 추가

- todo_app/search.py 에 제목 키워드 검색 함수 추가
- README 에 검색 사용 예시 추가
----------------------------------------
```

```text
--- PR Title ---
feat: 할 일 검색 기능 추가
--- PR Body ---
## Why
- 할 일이 많아지면 원하는 항목을 찾기 어려워 검색 기능이 필요했습니다.

## What
- todo_app/search.py 에 키워드로 제목을 찾는 search_todos() 추가
- README 에 검색 사용 예시 추가

## How to Test
- 할 일 2개를 추가한 뒤 search_todos("우유") 결과를 확인합니다.
- python main.py pr 출력이 Why/What/How to Test 구조인지 확인합니다.
----------------------------------------
```

형식이 맞아도 잘못된 파일을 언급하거나 실행하지 않은 테스트를 했다고 적을 수 있습니다. 제목이 잘리면서 핵심 단어가 빠질 수도 있습니다. Git diff와 대조해 설명이 사실인지 살피고, `How to Test`는 직접 따라 해 본 뒤 공유합니다.

## 변경 없음과 오류 처리

사무실에서 여러 부서가 문제의 원인을 파악하고 통합 민원 창구가 같은 양식으로 결과를 안내하는 것처럼, `ai_client.py`는 키 누락과 네트워크 문제를 원인이 담긴 `AIClientError` 계열의 예외로 전달합니다. `cli.py`의 `handle_cli_errors()`가 `main()`에서 올라온 AI 오류와 Git 오류를 한곳에서 받아, 커밋과 PR 명령 모두에서 원인을 `[ERROR]` 형식으로 표시하고 종료 코드 `1`을 돌려줍니다. 공통 처리 함수가 출력 형식과 실패 코드를 맡으므로 명령마다 안내를 따로 작성하다 기준이 달라지는 일을 줄일 수 있습니다. [오류를 받는 CLI 코드](ai_gitgen/cli.py#L66) · [네트워크 오류 처리](ai_gitgen/ai_client.py#L88)

| 상황 | 실제 처리 순서 | PowerShell에서 확인하는 방법 |
| --- | --- | --- |
| Git 변경사항 없음 | `collect_changes()`가 빈 파일 목록을 확인하면 `[INFO] 변경 사항이 없습니다.`를 표시하고 정상 종료합니다. 키 확인과 AI 호출보다 앞 단계입니다. | `demo 7`의 `clean` 시나리오 또는 아래 연습 명령 |
| API Key 없음 | 변경이 있어 AI 요청 단계에 진입하면 `get_api_key()`가 누락을 감지해 `MissingApiKeyError`를 보냅니다. `[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.`가 표시되며 요청은 발송되지 않습니다. | `demo 7`의 `feature` 시나리오 중 `API Key 없음` |
| 네트워크 연결 실패 | `send_http_request()`가 연결 오류를 `AIClientError`로 바꿉니다. CLI가 `[ERROR] AI API 네트워크 연결 실패: …`를 표시합니다. 직접 전달된 시간 초과는 별도 오류 메시지를 사용합니다. | `py -m unittest tests.practice.test_step5_ai_client.SendHttpRequestTest.test_network_error_becomes_client_error`로 모의 오류 확인 |

프로젝트를 막 내려받은 상태에서 `git status --short`가 비어 있다면, 해당 저장소에서 `commit`이나 `pr`을 실행해도 초안을 만들 변경이 없습니다. 초안 재료를 보려면 위의 `feature` 연습용 저장소를 사용하세요. 변경 없는 상태를 확실히 보여주려면 위 미리보기에서 만든 `$app`과 `$demoDir`을 그대로 사용해 다음 명령을 실행합니다.

```powershell
py -m learning_kit.practice_repo clean --path (Join-Path $demoDir 'clean')
Push-Location (Join-Path $demoDir 'clean')
git status --short
py $app commit --dry-run
Pop-Location
```

## 민감정보와 안전 모드

Git diff에는 새로 입력한 줄과 지운 줄이 모두 들어갑니다. 문서에서 지운 고객 이메일이나 비밀번호가 수정 대비표에는 남아 발송 자료에 포함되는 상황과 같습니다. `--safe-mode`는 `apply_safe_mode()`로 **diff 안의** 이메일 패턴과 `sk-`로 시작하는 키 패턴(뒤에 영문자·숫자·`_`·`-`가 16자 이상)을 `[MASKED]`로 바꿉니다. 이 옵션의 기본값은 꺼짐입니다. [마스킹 코드](ai_gitgen/safety.py#L10)

전화번호, 일반 비밀번호, 다른 접두사의 키는 diff에 남을 수 있습니다. 프롬프트에 별도로 들어가는 파일 목록과 PR 브랜치명은 가림 대상에서 빠져 있습니다. 파일 10개·200줄 같은 전송 제한도 현재 동작에 포함되지 않습니다. 실제 자료를 다룰 때는 `--safe-mode --dry-run`으로 화면에서 발송 내용을 확인하고, 민감한 정보가 남아 있으면 전송 전에 제외합니다. 시연이나 녹화에는 가짜 자료를 사용하세요.

**PowerShell에서 볼 부분**은 `py -m learning_kit.demo 3`의 마스킹 전후 또는 `demo 7`의 `secret` 시나리오입니다. `demo 3`의 전송 제한 예시에는 미구현 안내가 표시됩니다. `demo 7`에서는 `FakeTransport`가 받은 모의 프롬프트에 샘플 키가 그대로 들어갔는지도 확인할 수 있습니다. [마스킹 시연 코드](learning_kit/demo.py#L111)

## 실제 API 사용과 키 입력

실제 실행은 네이토의 Anthropic 호환 API `https://copa.codyssey.kr/v1/messages`와 기본 모델 `claude-haiku-4`를 사용합니다. API Key는 서비스가 요청 권한을 확인하는 출입증입니다. `get_api_key()`가 현재 실행 환경의 `AI_API_KEY`를 읽으므로, 키 원문을 코드·README·`.env` 같은 파일이나 Git 기록에 남기지 마세요. 오프라인 시연에는 이 설정을 건너뜁니다. [API 설정](ai_gitgen/config.py#L3)

Windows PowerShell에서 아래 순서로 입력합니다. [PowerShell 숨김 입력 문서](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/read-host?view=powershell-5.1#-assecurestring)

1. 아래 블록의 첫 줄만 복사해 PowerShell에서 실행합니다.
2. `네이토 API Key:`가 표시되면 발급 화면에서 키 원문만 복사합니다. 숨김 입력 칸에 따옴표와 줄바꿈 없이 키 한 줄을 붙여넣고 Enter를 누릅니다. 입력은 별표로 표시됩니다. 붙여넣기가 동작하지 않으면 별도의 PowerShell 창에서 첫 줄부터 다시 시작하거나 숨김 입력 칸에 직접 입력하세요.
3. 일반 명령 프롬프트로 돌아오면 나머지 두 줄을 복사해 실행합니다. 키 확인을 위해 환경변수 값을 화면에 출력하거나 키 원문을 파일에 저장하지 마세요.

```powershell
$natoApiKey = Read-Host '네이토 API Key' -AsSecureString
$env:AI_API_KEY = $([System.Net.NetworkCredential]::new('', $natoApiKey).Password)
Remove-Variable natoApiKey
```

이렇게 설정한 환경변수는 해당 PowerShell 세션과 거기서 실행한 Python에 전달됩니다. 실제 실행은 키를 설정한 **같은 창**에서, 변경사항이 있는 프로젝트 폴더로 이동한 뒤 진행합니다. 본인에게 필요한 초안 명령을 선택합니다. 각 명령은 실제 API를 호출할 수 있으며 토큰 사용과 요금이 발생할 수 있습니다. [PowerShell 환경변수 문서](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables?view=powershell-5.1)

```powershell
py main.py commit --safe-mode
py main.py pr --safe-mode
```

`python` 명령을 사용하는 환경에서는 `python main.py commit --safe-mode` 또는 `python main.py pr --safe-mode`로 실행합니다. 사용을 마치면 PowerShell 창을 닫거나 `Remove-Item Env:AI_API_KEY`로 현재 세션에서 키를 지웁니다. 실제 네이토 API 연동으로 커밋 메시지와 PR 초안 생성을 확인했습니다.

## 팀에서 먼저 개선할 기능

팀 프로젝트에 적용한다면 **외부 전송 전 검사**를 먼저 강화하겠습니다. 파일 목록과 브랜치명을 포함한 전체 프롬프트에서 팀이 쓰는 키 패턴과 고객 식별 정보를 확인하고, 의심되는 항목이 있으면 발송을 멈춘 뒤 사용자가 처리할 수 있게 하는 기능입니다. 잘못 작성된 초안은 공유 전에 고칠 수 있지만, 이미 외부에 보낸 고객 정보나 키를 되돌려 받을 수는 없기 때문입니다.

그다음은 **전송 크기 제한**입니다. 팀의 큰 변경을 한꺼번에 보내면 비용이 늘고 중요한 변경이 묻힐 수 있습니다. 큰 diff는 사용자에게 먼저 크기를 알리고 어떤 부분을 전송할지 선택할 수 있게 한 뒤, 제목이나 PR 구획의 품질 개선을 진행할 수 있습니다.

## 자동 테스트와 참고 자료

자동 테스트는 예시 입력의 처리 결과를 예상값과 비교하는 도구입니다. 아래 명령은 키와 실제 AI 연결 없이 실행합니다.

```powershell
py -m learning_kit.practice base
py -m learning_kit.practice 7
py -m learning_kit.practice 8
```

| 자료 | 찾을 수 있는 내용 |
| --- | --- |
| [START_HERE.md](START_HERE.md) · [실습 단계](docs/PRACTICE_STEPS.md) | 연습 자료와 단계별 실행 방법 |
| [학습 안내서](docs/B3-2_STUDY_GUIDE.html) · [프로그램 구조](docs/architecture.md) | 처리 흐름과 설계 배경 |
| [모듈 문서](docs/modules/) · [요구사항 분석](docs/REQUIREMENTS_ANALYSIS.md) | 함수별 역할과 출력 형식의 기준 |
| [learning_kit](learning_kit/) · [tests](tests/) | 모의 실행 도구와 자동 테스트 |
