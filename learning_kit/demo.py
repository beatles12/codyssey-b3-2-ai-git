"""단계별 데모 — 내가 구현한 함수의 결과를 눈으로 확인한다. (✅ 구현됨)

사용법
    python -m learning_kit.demo 1                        # Step 1 데모
    python -m learning_kit.demo 1 pr --temperature 0.9   # 내 옵션으로 실험
    python -m learning_kit.demo 5                        # 가짜 AI 로 요청/응답 보기
    python -m learning_kit.demo 7                        # 전체 흐름 모의 실행

- 실제 AI API 는 절대 부르지 않습니다. (가짜 AI: learning_kit/fake_ai.py)
- 아직 구현하지 않은 함수는 [TODO] 로 표시하고 다음 항목으로 넘어갑니다.
- 자동 채점은 python -m learning_kit.practice <단계> 로 하세요.
"""

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from unittest import mock

from learning_kit.paths import PRACTICE_REPO_DIR, PROJECT_ROOT
from learning_kit.paths import read_practice_file

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FAKE_KEY = 'demo-key-not-real'


def title(text):
    print()
    print('=' * 70)
    print(f' {text}')
    print('=' * 70)


def show(label, func, *args, **kwargs):
    """함수를 실행해 결과를 보여 준다. TODO/오류는 안내만 하고 계속한다."""
    print(f'\n>>> {label}')
    try:
        value = func(*args, **kwargs)
    except NotImplementedError as error:
        print(f'[TODO] 아직 비어 있습니다: {error}')
        return None
    except SystemExit as error:
        print(f'(SystemExit 발생, 종료 코드 {error.code}) '
              '— argparse 가 잘못된 입력을 거부했습니다.')
        return None
    except Exception as error:  # 학습 중 생긴 오류를 친절하게 보여 주기
        print(f'[오류] {type(error).__name__}: {error}')
        last = traceback.extract_tb(error.__traceback__)[-1]
        print(f'       위치: {last.filename}:{last.lineno}')
        return None
    if isinstance(value, str):
        print(value if value else "'' (빈 문자열)")
    else:
        print(repr(value))
    return value


def ensure_practice_repo(scenario='feature'):
    from learning_kit.practice_repo import create_practice_repo
    if not (PRACTICE_REPO_DIR / '.git').exists():
        print(f'[INFO] 연습 저장소가 없어 새로 만듭니다: {scenario}')
        create_practice_repo(PRACTICE_REPO_DIR, scenario)
    return PRACTICE_REPO_DIR


# ---------------------------------------------------------------------------
def demo_step1(extra):
    from ai_gitgen import cli
    title('Step 1 · build_parser() / validate_options()')
    samples = [extra] if extra else [
        ['commit'],
        ['pr', '--model', 'my-model', '--temperature', '0.7',
         '--max-tokens', '300', '--safe-mode'],
        ['commit', '--temperature', '1.5'],
        ['commit', '--max-tokens', 'abc'],
        [],
    ]
    for argv in samples:
        args = show(f'build_parser().parse_args({argv})',
                    lambda a=argv: cli.build_parser().parse_args(a))
        if args is not None:
            show('validate_options(args)', cli.validate_options, args)


def demo_step2(_extra):
    from ai_gitgen import git_collector as gc
    title('Step 2 · Git 변경 사항 수집')
    show('parse_status_output(practice_data/git_status_sample.txt)',
         gc.parse_status_output, read_practice_file('git_status_sample.txt'))
    repo = ensure_practice_repo()
    print(f'\n[INFO] 아래는 연습 저장소({repo})에서 실행한 결과입니다.')
    show("run_git(['--version'])", gc.run_git, ['--version'])
    show('is_git_repository(연습 저장소)', gc.is_git_repository, repo)
    with tempfile.TemporaryDirectory() as empty_dir, \
            mock.patch.dict(os.environ, {'GIT_CEILING_DIRECTORIES':
                                         os.path.dirname(empty_dir)}):
        show('is_git_repository(빈 임시 폴더)', gc.is_git_repository,
             empty_dir)
    show('get_current_branch()', gc.get_current_branch, repo)
    show('get_changed_files()', gc.get_changed_files, repo)
    diff = show('get_diff()', gc.get_diff, repo)
    if diff is not None:
        show('count_diff_lines(diff)', gc.count_diff_lines, diff)


def demo_step3(_extra):
    from ai_gitgen import safety
    title('Step 3 · 안전 모드 (마스킹 / 전송 제한)')
    secret_diff = read_practice_file('git_diff_with_secrets.diff')
    print('\n[원본] practice_data/git_diff_with_secrets.diff')
    print(secret_diff)
    show('mask_sensitive(원본)', safety.mask_sensitive, secret_diff)

    big = ''.join(
        f'diff --git a/f{n}.py b/f{n}.py\n' + ''.join(
            f'+line {i}\n' for i in range(30))
        for n in range(15))
    print(f'\n[원본] 가짜 큰 diff: 파일 15개, {len(big.splitlines())}줄')
    limited = show('limit_diff(큰 diff) 의 앞 5줄과 끝 3줄만 표시',
                   lambda: _head_tail(safety.limit_diff(big)))
    if limited is not None:
        result = safety.limit_diff(big)
        print(f'  -> 결과 줄 수: {len(result.splitlines())}, '
              f"파일 수: {result.count('diff --git ')}")
    show('apply_safe_mode(원본, enabled=False) 가 원본과 같은가?',
         lambda: safety.apply_safe_mode(secret_diff, False) == secret_diff)


def _head_tail(text):
    lines = text.splitlines()
    return '\n'.join(lines[:5] + ['   ...'] + lines[-3:])


def demo_step4(_extra):
    from ai_gitgen import git_collector as gc
    from ai_gitgen import prompt_builder as pb
    title('Step 4 · 프롬프트 만들기')
    try:
        files = gc.parse_status_output(
            read_practice_file('git_status_sample.txt'))[:3]
    except NotImplementedError:
        files = [{'code': 'M', 'path': 'README.md'},
                 {'code': 'M', 'path': 'todo_app/app.py'},
                 {'code': 'A', 'path': 'todo_app/search.py'}]
        print('[INFO] Step 2 가 아직이라 파일 목록은 미리 정한 값을 씁니다.')
    diff = read_practice_file('git_diff_sample.diff')
    show('format_file_list(files)', pb.format_file_list, files)
    commit = show('build_commit_prompt(files, diff)',
                  pb.build_commit_prompt, files, diff)
    pr = show("build_pr_prompt(files, diff, 'feature/add-search')",
              pb.build_pr_prompt, files, diff, 'feature/add-search')
    for name, prompt in (('커밋', commit), ('PR', pr)):
        if prompt:
            print(f'\n[INFO] {name} 프롬프트: {len(prompt)}글자, '
                  f'{len(prompt.splitlines())}줄')
    print('[생각해 보기] 글자 수가 늘면 요청 비용(입력 토큰)도 늘어납니다.')


def demo_step5(_extra):
    from ai_gitgen import ai_client, config
    from learning_kit.fake_ai import FakeTransport
    title('Step 5 · AI API 요청/응답 (가짜 AI 사용, 실제 호출 없음)')
    show('build_headers(가짜키)', ai_client.build_headers, FAKE_KEY)
    show("build_request_body('안녕', model, 0.3, 300)",
         ai_client.build_request_body, '안녕', config.DEFAULT_MODEL,
         0.3, 300)
    response = json.loads(read_practice_file(
        'api_responses/anthropic_commit.json'))
    show('extract_text(anthropic_commit.json)', ai_client.extract_text,
         response)

    fake = FakeTransport()
    show('call_ai_api(..., api_key=가짜키, transport=FakeTransport())',
         ai_client.call_ai_api, '커밋 메시지를 만들어 줘',
         config.DEFAULT_MODEL, 0.3, 300, api_key=FAKE_KEY, transport=fake)
    print(f'\n[INFO] 가짜 AI 호출 횟수: {fake.call_count}')
    if fake.calls:
        call = fake.calls[0]
        headers = {k: ('***' if FAKE_KEY in str(v) else v)
                   for k, v in call['headers'].items()}
        print(f"[INFO] 보낸 주소: {call['url']}")
        print(f'[INFO] 보낸 헤더(키는 *** 로 가림): {headers}')
        print('[INFO] 보낸 본문:')
        print(json.dumps(call['body'], ensure_ascii=False, indent=2))

    with mock.patch.dict(os.environ, {}, clear=False):
        os.environ.pop('AI_API_KEY', None)
        show('get_api_key()  (환경변수 없음 -> MissingApiKeyError 예상)',
             _expect_error, ai_client.get_api_key)
    error = ai_client.AIClientError('AI API 요청 실패 (HTTP 401): '
                                    'invalid x-api-key')
    show('call_ai_api(...) with 401 흉내 -> AIClientError 예상',
         _expect_error, ai_client.call_ai_api, 'x', 'm', 0.3, 10,
         api_key=FAKE_KEY, transport=FakeTransport(error=error))


def _expect_error(func, *args, **kwargs):
    try:
        value = func(*args, **kwargs)
    except NotImplementedError:
        raise
    except Exception as error:
        return f'예상대로 {type(error).__name__}: {error}'
    return f'(예외가 나지 않았습니다. 반환값: {value!r})'


def demo_step6(_extra):
    from ai_gitgen import formatter as fm
    from learning_kit.fake_ai import FAKE_LONG_TITLE_TEXT, FAKE_PR_TEXT
    from learning_kit.fake_ai import FAKE_BROKEN_PR_TEXT, FAKE_COMMIT_TEXT
    title('Step 6 · 출력 검증과 다듬기')
    show('split_title_body(FAKE_COMMIT_TEXT)', fm.split_title_body,
         FAKE_COMMIT_TEXT)
    long_title = FAKE_LONG_TITLE_TEXT.splitlines()[0]
    print(f'\n[INFO] 긴 제목 길이: {len(long_title)}글자')
    short = show('shorten_title(긴 제목, 72)', fm.shorten_title,
                 long_title, 72)
    if isinstance(short, str):
        print(f'  -> 줄인 뒤 길이: {len(short)}글자')
    show('validate_commit_message(FAKE_COMMIT_TEXT)',
         fm.validate_commit_message, FAKE_COMMIT_TEXT)
    show('validate_commit_message(긴 제목 메시지)',
         fm.validate_commit_message, FAKE_LONG_TITLE_TEXT)
    pr_body = FAKE_PR_TEXT.split('\n', 1)[1].strip()
    show('validate_pr_body(정상 PR 본문)', fm.validate_pr_body, pr_body)
    broken = FAKE_BROKEN_PR_TEXT.split('\n', 1)[1].strip()
    show('validate_pr_body(섹션 빠진 본문)', fm.validate_pr_body, broken)
    show('format_commit_output(FAKE_COMMIT_TEXT)',
         fm.format_commit_output, FAKE_COMMIT_TEXT)
    show('format_pr_output(제목, 본문)', fm.format_pr_output,
         FAKE_PR_TEXT.splitlines()[0], pr_body)


def demo_step7(extra):
    from ai_gitgen import cli
    from learning_kit.fake_ai import FakeTransport
    from learning_kit.practice_repo import create_practice_repo
    title('Step 7 · 전체 흐름 모의 실행 (가짜 AI, 임시 연습 저장소)')
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        cases = [
            ('feature', ['commit'] + extra, True),
            ('feature', ['pr'] + extra, True),
            ('clean', ['commit'], True),
            ('feature', ['commit'], False),
            ('secret', ['commit', '--safe-mode'], True),
        ]
        for scenario, argv, with_key in cases:
            repo = create_practice_repo(Path(tmp) / scenario, scenario)
            fake = FakeTransport()
            key_text = 'API Key 있음(가짜)' if with_key else 'API Key 없음'
            print(f'\n### 시나리오={scenario}, 명령={argv}, {key_text}')
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop('AI_API_KEY', None)
                if with_key:
                    os.environ['AI_API_KEY'] = FAKE_KEY
                code = show('main(...) 실행 결과(종료 코드)', cli.main,
                            argv, cwd=str(repo), transport=fake)
            print(f'[INFO] 종료 코드={code}, 가짜 AI 호출 횟수='
                  f'{fake.call_count}')
            if scenario == 'secret' and fake.calls:
                leaked = 'sk-fake-practice' in fake.sent_text()
                print(f'[INFO] 가짜 키가 AI 로 전송되었나? {leaked} '
                      '(False 여야 안전)')


def demo_step8(_extra):
    from tests.practice.test_step8_readme import README_RECOMMENDED
    from tests.practice.test_step8_readme import README_REQUIREMENTS
    title('Step 8 · README 제출 기준 점검')
    readme = (PROJECT_ROOT / 'README.md').read_text(encoding='utf-8')
    if 'TODO(Step 8)' in readme:
        print('[TODO] README.md 에 아직 TODO(Step 8) 표시가 있습니다.')
    if '✏️' in readme:
        print('[TODO] README.md 에 아직 채우지 않은 ✏️ 칸이 있습니다.')
    for group, items in (('필수', README_REQUIREMENTS),
                         ('선택', README_RECOMMENDED)):
        print(f' [{group}]')
        for label, words in items:
            ok = any(word.lower() in readme.lower() for word in words)
            mark = '[통과]' if ok else '[부족]'
            print(f'  {mark} {label}  (찾는 단어: {", ".join(words)})')


DEMOS = {
    1: demo_step1, 2: demo_step2, 3: demo_step3, 4: demo_step4,
    5: demo_step5, 6: demo_step6, 7: demo_step7, 8: demo_step8,
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or not argv[0].isdigit() or int(argv[0]) not in DEMOS:
        print('사용법: python -m learning_kit.demo <단계 1~8> [추가 옵션]')
        print('예)    python -m learning_kit.demo 1 pr --temperature 0.9')
        return 2
    # 데모 중에는 실제 네트워크 호출을 막는다.
    blocked = RuntimeError('데모에서는 실제 네트워크 호출이 금지되어 있습니다.')
    with mock.patch('urllib.request.urlopen', side_effect=blocked), \
            mock.patch('socket.create_connection', side_effect=blocked):
        DEMOS[int(argv[0])](argv[1:])
    print()
    print(f'[INFO] 자동 채점: python -m learning_kit.practice {argv[0]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
