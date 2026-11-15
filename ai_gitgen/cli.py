
"""명령줄 처리와 전체 업무 흐름 연결 (Step 1, 7)."""

import argparse
import functools
import sys

from ai_gitgen import ai_client, config, formatter
from ai_gitgen import git_collector, prompt_builder, safety


def log(level, message):
    """실행 상태와 오류 메시지를 출력한다."""
    stream = sys.stderr if level == 'ERROR' else sys.stdout
    print(f'[{level}] {message}', file=stream)


def build_parser():
    """commit, pr 명령과 옵션을 등록한다."""
    parser = argparse.ArgumentParser(
        description='AI 커밋 메시지 및 PR 초안 생성기'
    )
    commands = parser.add_subparsers(
        dest='command', required=True
    )

    for name in ('commit', 'pr'):
        command = commands.add_parser(name)
        command.add_argument(
            '--model', default=config.DEFAULT_MODEL
        )
        command.add_argument(
            '--temperature', type=float,
            default=config.DEFAULT_TEMPERATURE
        )
        command.add_argument(
            '--max-tokens', type=int,
            default=config.DEFAULT_MAX_TOKENS
        )
        command.add_argument(
            '--safe-mode', action='store_true'
        )
        command.add_argument(
            '--dry-run', action='store_true'
        )

    return parser


def validate_options(args):
    """입력한 옵션 값의 문제를 확인한다."""
    problems = []

    if not args.model.strip():
        problems.append('model: 모델 이름을 입력하세요.')

    if not config.TEMPERATURE_MIN <= args.temperature <= config.TEMPERATURE_MAX:
        problems.append('temperature: 허용 범위는 0.0~1.0입니다.')

    if not config.MAX_TOKENS_MIN <= args.max_tokens <= config.MAX_TOKENS_LIMIT:
        problems.append('max_tokens: 허용 범위는 1~4096입니다.')

    return problems


def handle_cli_errors(func):
    """Git과 AI 관련 오류를 한곳에서 처리한다."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (git_collector.GitCommandError,
                ai_client.AIClientError) as error:
            log('ERROR', str(error))
            return 1

    return wrapper


def collect_changes(args, cwd):
    """Git 변경사항을 수집하고 안전 모드를 적용한다."""
    if not git_collector.is_git_repository(cwd):
        raise git_collector.GitCommandError(
            'Git 저장소가 아닙니다. 작업 폴더를 확인하세요.'
        )

    changed_files = git_collector.get_changed_files(cwd)

    if not changed_files:
        log('INFO', '변경 사항이 없습니다.')
        return None

    diff_text = git_collector.get_diff(cwd)
    line_count = git_collector.count_diff_lines(diff_text)

    log('INFO', f'변경 파일: {len(changed_files)}개')
    log('INFO', f'Git diff: {line_count}줄')

    if args.safe_mode:
        diff_text = safety.apply_safe_mode(diff_text, True)
        log('INFO', '안전 모드: 일부 민감정보를 마스킹했습니다.')

    return changed_files, diff_text


def request_ai(prompt, args, transport):
    """AI에 한 번 요청하고 생성된 글을 반환한다."""
    result = ai_client.call_ai_api(
        prompt,
        args.model,
        args.temperature,
        args.max_tokens,
        transport=transport,
    )
    log('INFO', 'AI API 호출 횟수: 1')
    return result


def run_commit(args, cwd=None, transport=None):
    """Git 변경사항으로 커밋 메시지를 생성한다."""
    collected = collect_changes(args, cwd)

    if collected is None:
        return 0

    changed_files, diff_text = collected
    prompt = prompt_builder.build_commit_prompt(
        changed_files, diff_text
    )

    if args.dry_run:
        log('INFO', '미리보기: AI API를 호출하지 않습니다.')
        print(prompt)
        return 0

    response = request_ai(prompt, args, transport)
    title, body = formatter.split_title_body(response)

    title = formatter.shorten_title(
        title, config.COMMIT_TITLE_MAX
    )
    message = title + ('\n\n' + body if body else '')

    paths = [item['path'] for item in changed_files]
    problems = formatter.validate_commit_message(
        message, paths
    )

    for problem in problems:
        log('WARN', problem)

    print(formatter.format_commit_output(message))
    return 0


def run_pr(args, cwd=None, transport=None):
    """Git 변경사항으로 PR 제목과 본문을 생성한다."""
    collected = collect_changes(args, cwd)

    if collected is None:
        return 0

    changed_files, diff_text = collected
    branch_name = git_collector.get_current_branch(cwd)
    log('INFO', f'현재 브랜치: {branch_name}')

    prompt = prompt_builder.build_pr_prompt(
        changed_files, diff_text, branch_name
    )

    if args.dry_run:
        log('INFO', '미리보기: AI API를 호출하지 않습니다.')
        print(prompt)
        return 0

    response = request_ai(prompt, args, transport)
    title, body = formatter.split_title_body(response)

    title = formatter.shorten_title(
        title, config.PR_TITLE_MAX
    )

    problems = (
        formatter.validate_pr_title(title)
        + formatter.validate_pr_body(body)
    )

    for problem in problems:
        log('WARN', problem)

    print(formatter.format_pr_output(title, body))
    return 0


@handle_cli_errors
def main(argv=None, cwd=None, transport=None):
    """명령을 해석하고 해당 업무를 실행한다."""
    args = build_parser().parse_args(argv)
    problems = validate_options(args)

    if problems:
        for problem in problems:
            log('ERROR', problem)
        return 2

    if args.command == 'commit':
        return run_commit(args, cwd, transport)

    return run_pr(args, cwd, transport)
