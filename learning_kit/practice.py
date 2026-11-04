"""단계별 연습 테스트 실행기. (✅ 구현됨)

사용법
    python -m learning_kit.practice            # 전체 진행 현황표
    python -m learning_kit.practice 2          # Step 2 연습 테스트 자세히
    python -m learning_kit.practice 2 -v       # 실패한 테스트의 전체 오류 보기
    python -m learning_kit.practice base       # 기본 환경 테스트 (지금 통과해야 함)
    python -m learning_kit.practice all        # 모든 단계 자세히

결과 읽는 법
    [통과]  테스트가 확인하는 조건을 만족했습니다.
    [TODO]  아직 raise NotImplementedError 가 남아 있습니다. (구현 전)
    [실패]  구현은 했지만 결과가 기대와 다릅니다. 메시지를 읽어 보세요.
    [오류]  코드 실행 중 예상하지 못한 예외가 났습니다. -v 로 자세히 보세요.
    (선택)  이름에 optional 이 붙은 테스트. 통과하지 않아도 미션 필수는 아님.

같은 테스트를 표준 방식으로 돌릴 수도 있습니다.
    python -m unittest discover -s tests/practice -t .
"""

import argparse
import sys
import traceback
import unicodedata
import unittest

from learning_kit.paths import PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STEPS = {
    1: ('test_step1_cli_options', 'CLI 옵션 만들기·입력값 검사',
        'ai_gitgen/cli.py'),
    2: ('test_step2_git_collector', 'Git 변경 사항 수집',
        'ai_gitgen/git_collector.py'),
    3: ('test_step3_safety', '안전 모드: 마스킹·전송 제한',
        'ai_gitgen/safety.py'),
    4: ('test_step4_prompt', '프롬프트 만들기',
        'ai_gitgen/prompt_builder.py'),
    5: ('test_step5_ai_client', 'AI API 요청·응답·오류 처리',
        'ai_gitgen/ai_client.py'),
    6: ('test_step6_formatter', '출력 검증·다듬기',
        'ai_gitgen/formatter.py'),
    7: ('test_step7_flow', '전체 흐름 연결 (commit / pr)',
        'ai_gitgen/cli.py'),
    8: ('test_step8_readme', 'README 작성·제출 준비', 'README.md'),
}

LABELS = {
    'pass': '[통과]',
    'todo': '[TODO]',
    'fail': '[실패]',
    'error': '[오류]',
    'skip': '[건너뜀]',
}


def _pad(text, width):
    """한글처럼 화면에서 두 칸을 차지하는 글자를 고려해 오른쪽을 공백으로 채운다."""
    shown = sum(2 if unicodedata.east_asian_width(ch) in 'WF' else 1
                for ch in text)
    return text + ' ' * max(width - shown, 0)


def _is_todo(exc_type):
    return exc_type is not None and issubclass(exc_type, NotImplementedError)


def _first_line(err):
    exc_type, exc_value, _tb = err
    text = str(exc_value).strip().splitlines()
    detail = text[0] if text else ''
    return f'{exc_type.__name__}: {detail}'.strip()


# 한 테스트 안에서 여러 결과가 나오면(subTest) 가장 나쁜 결과로 표시한다.
SEVERITY = {'pass': 0, 'skip': 1, 'todo': 2, 'fail': 3, 'error': 4}


def _line_number(test):
    """테스트 메서드가 파일에서 몇 번째 줄에 있는지 (정의 순서 정렬용)."""
    method = getattr(type(test), getattr(test, '_testMethodName', ''), None)
    code = getattr(method, '__code__', None)
    return code.co_firstlineno if code else 0


class FriendlyResult(unittest.TestResult):
    """테스트 결과를 통과/TODO/실패/오류로 나눠, 테스트 1개당 1줄로 기록한다."""

    def __init__(self):
        super().__init__()
        self._by_id = {}

    @property
    def records(self):
        return sorted(
            self._by_id.values(),
            key=lambda r: ('' if r['test'] is None
                           else type(r['test']).__module__,
                           0 if r['test'] is None
                           else _line_number(r['test'])))

    def add_record(self, test, status, detail='', full=''):
        key = test.id() if test is not None else f'load-error-{detail}'
        old = self._by_id.get(key)
        if old is None or SEVERITY[status] > SEVERITY[old['status']]:
            self._by_id[key] = {'test': test, 'status': status,
                                'detail': detail, 'traceback': full}

    def _record(self, test, status, err=None, prefix=''):
        detail = _first_line(err) if err else ''
        full = ''.join(traceback.format_exception(*err)) if err else ''
        self.add_record(test, status, f'{prefix}{detail}', full)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, 'pass')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, 'todo' if _is_todo(err[0]) else 'fail', err)

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, 'todo' if _is_todo(err[0]) else 'error', err)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is None:
            return
        if _is_todo(err[0]):
            status = 'todo'
        elif issubclass(err[0], test.failureException):
            status = 'fail'
        else:
            status = 'error'
        self._record(test, status, err, prefix=f'{subtest._subDescription()} ')

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.add_record(test, 'skip', reason)


def _is_optional(test):
    return '_optional_' in test.id() or test.id().endswith('_optional')


def _description(test):
    doc = test.shortDescription()
    if doc:
        return doc
    return test.id().rsplit('.', 1)[-1]


def run_module(module_name):
    """tests 아래의 모듈 하나를 실행해 FriendlyResult 를 돌려준다."""
    loader = unittest.TestLoader()
    try:
        suite = loader.loadTestsFromName(module_name)
    except Exception as error:  # 테스트 파일 자체를 불러오지 못한 경우
        result = FriendlyResult()
        result.add_record(None, 'error',
                          f'{module_name} 을(를) 불러오지 못했습니다: {error}',
                          traceback.format_exc())
        return result
    result = FriendlyResult()
    suite.run(result)
    return result


def summarize(result):
    """필수/선택 테스트별 개수를 센다."""
    summary = {
        'required': {'pass': 0, 'todo': 0, 'fail': 0, 'error': 0,
                     'skip': 0},
        'optional': {'pass': 0, 'todo': 0, 'fail': 0, 'error': 0,
                     'skip': 0},
    }
    for record in result.records:
        test = record['test']
        group = 'optional' if test is not None and _is_optional(test) \
            else 'required'
        summary[group][record['status']] += 1
    return summary


def _step_state(summary):
    required = summary['required']
    total = sum(required.values()) - required['skip']
    if total == 0:
        return '테스트 없음'
    if required['pass'] == total:
        return '완료'
    if required['todo'] == total:
        return 'TODO'
    return '진행 중'


def print_detail(title, result, verbose=False):
    print('=' * 70)
    print(f' {title}')
    print('=' * 70)
    for group_name, want_optional in (('필수', False), ('선택', True)):
        rows = [r for r in result.records
                if (r['test'] is not None and _is_optional(r['test']))
                == want_optional]
        if not rows:
            continue
        print(f' [{group_name} 테스트]')
        for record in rows:
            label = LABELS[record['status']]
            name = (_description(record['test'])
                    if record['test'] is not None else '테스트 불러오기')
            print(f'  {label} {name}')
            if record['status'] in ('fail', 'error'):
                print(f'         -> {record["detail"]}')
                if verbose:
                    for line in record['traceback'].rstrip().splitlines():
                        print(f'            {line}')
            elif record['status'] == 'todo' and verbose:
                print(f'         -> {record["detail"]}')
    summary = summarize(result)
    req = summary['required']
    opt = summary['optional']
    print('-' * 70)
    print(f'  필수: 통과 {req["pass"]} / TODO {req["todo"]} / '
          f'실패 {req["fail"]} / 오류 {req["error"]}')
    if sum(opt.values()):
        print(f'  선택: 통과 {opt["pass"]} / 미완료 '
              f'{opt["todo"] + opt["fail"] + opt["error"]}')
    return summary


def run_step(number, verbose=False):
    module, name, target = STEPS[number]
    result = run_module(f'tests.practice.{module}')
    summary = print_detail(f'Step {number} · {name}   (수정할 파일: {target})',
                           result, verbose)
    state = _step_state(summary)
    if state == '완료':
        print(f'  ★ Step {number} 필수 테스트를 모두 통과했습니다! '
              '변경 사항을 커밋해 두세요.')
    else:
        print(f'  ➜ 힌트: docs/B3-2_STUDY_GUIDE.html#step{number} '
              f'또는 docs/PRACTICE_STEPS.md 의 Step {number}')
    print()
    return summary


def run_base(verbose=False):
    loader = unittest.TestLoader()
    suite = loader.discover(str(PROJECT_ROOT / 'tests' / 'base'),
                            top_level_dir=str(PROJECT_ROOT))
    result = FriendlyResult()
    suite.run(result)
    summary = print_detail('기본 환경 테스트 (tests/base) — 지금 통과해야 합니다',
                           result, verbose)
    req = summary['required']
    ok = req['fail'] == 0 and req['error'] == 0 and req['todo'] == 0
    if ok:
        print('  ★ 실습 환경이 준비되었습니다. Step 1 부터 시작하세요.')
    else:
        print('  ➜ 환경 문제를 먼저 해결하세요. START_HERE.md 의 '
              '"문제가 생겼을 때" 참고')
    print()
    return ok


def print_overview():
    print('=' * 70)
    print(' B3-2 연습 진행 현황 (필수 테스트 기준)')
    print('=' * 70)
    print(f' {_pad("단계", 5)} {_pad("내용", 34)} {_pad("통과/전체", 11)} 상태')
    next_step = None
    for number, (module, name, _target) in STEPS.items():
        result = run_module(f'tests.practice.{module}')
        summary = summarize(result)
        req = summary['required']
        total = sum(req.values()) - req['skip']
        state = _step_state(summary)
        if state != '완료' and next_step is None:
            next_step = number
        score = f'{req["pass"]:>3} / {total}'
        print(f'  {number:<4} {_pad(name, 34)} {_pad(score, 11)} {state}')
    print('-' * 70)
    if next_step is None:
        print('  ★ 모든 단계의 필수 테스트를 통과했습니다!')
        print('    Step 8 의 "실제 API 1회 확인"과 제출 체크리스트를 '
              '진행하세요.')
    else:
        print(f'  ➜ 다음 할 일: python -m learning_kit.practice {next_step}')
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='python -m learning_kit.practice',
        description='B3-2 단계별 연습 테스트를 실행합니다.')
    parser.add_argument('target', nargs='?', default='overview',
                        help='단계 번호(1~8), base, all 중 하나')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='오류의 전체 내용(Traceback)까지 보기')
    args = parser.parse_args(argv)

    if args.target == 'overview':
        print_overview()
        return 0
    if args.target == 'base':
        return 0 if run_base(args.verbose) else 1
    if args.target == 'all':
        for number in STEPS:
            run_step(number, args.verbose)
        return 0
    if args.target.isdigit() and int(args.target) in STEPS:
        summary = run_step(int(args.target), args.verbose)
        return 0 if _step_state(summary) == '완료' else 1
    parser.error('단계 번호(1~8), base, all 중 하나를 입력하세요.')
    return 2


if __name__ == '__main__':
    sys.exit(main())
