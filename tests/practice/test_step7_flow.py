"""Step 7 연습 테스트 — 전체 흐름 연결 (ai_gitgen/cli.py 의 main/run_*)

실행: python -m learning_kit.practice 7

공식 체크리스트 항목 1을 자동으로 확인한다. (가짜 AI 사용, 실제 호출 없음)
    - commit 명령 -> 커밋 메시지 출력
    - pr 명령 -> PR 제목/본문 출력 (Why/What/How to Test + 불릿)
    - API Key 없음 -> 오류 메시지 후 종료
    - 변경 없음 -> "변경 사항이 없습니다"
    - 출력이 길이/형식 규칙을 만족
"""

import json
import os
import unittest

from ai_gitgen import cli, config
from learning_kit.fake_ai import FAKE_LONG_TITLE_TEXT, FAKE_PR_TEXT
from learning_kit.fake_ai import FakeTransport
from tests.helpers import FAKE_KEY, PracticeTestCase, has_separator
from tests.helpers import line_after


class FlowTestCase(PracticeTestCase):

    def run_cli(self, argv, scenario='feature', key=True, transport=None,
                repo=None):
        """연습 저장소에서 cli.main() 을 실행하고 (코드, 출력, 가짜AI) 반환."""
        repo = repo or self.make_repo(scenario)
        fake = transport or FakeTransport()
        if key:
            os.environ['AI_API_KEY'] = FAKE_KEY
        with self.inside(repo):
            code, output = self.capture(cli.main, argv, cwd=repo,
                                        transport=fake)
        return code, output, fake


class CommitFlowTest(FlowTestCase):

    def test_commit_prints_message(self):
        """commit: 로그 + 'Commit Message' 구획 + 제목이 출력되고 종료 코드 0"""
        code, output, fake = self.run_cli(['commit'])
        self.assertEqual(code, 0, output)
        self.assertIn('[INFO]', output)
        self.assertEqual(line_after(output, 'Commit Message'),
                         'feat: 할 일 검색 기능 추가')
        self.assertTrue(has_separator(output))

    def test_commit_calls_ai_once(self):
        """commit: AI 호출은 정확히 1회 (비용 관리)"""
        _code, _output, fake = self.run_cli(['commit'])
        self.assertEqual(fake.call_count, 1)

    def test_commit_sends_changes_to_ai(self):
        """commit: 변경 파일과 diff 내용이 AI 요청에 들어간다"""
        _code, _output, fake = self.run_cli(['commit'])
        sent = fake.sent_text()
        self.assertIn('todo_app/search.py', sent)
        self.assertIn('complete_todo', sent)

    def test_cli_options_reach_request(self):
        """--model / --temperature / --max-tokens 값이 요청 본문에 들어간다"""
        _code, _output, fake = self.run_cli(
            ['commit', '--model', 'my-model', '--temperature', '0.9',
             '--max-tokens', '123'])
        body = fake.calls[0]['body']
        self.assertEqual(body['model'], 'my-model')
        self.assertEqual(body['temperature'], 0.9)
        self.assertEqual(body['max_tokens'], 123)

    def test_long_commit_title_is_fixed(self):
        """AI 가 72자 넘는 제목을 줘도 최종 출력 제목은 72자 이하"""
        fake = FakeTransport(text=FAKE_LONG_TITLE_TEXT)
        code, output, _fake = self.run_cli(['commit'], transport=fake)
        self.assertEqual(code, 0, output)
        title = line_after(output, 'Commit Message')
        self.assertIsNotNone(title, output)
        self.assertLessEqual(len(title), config.COMMIT_TITLE_MAX)
        self.assertLessEqual(fake.call_count, 2)

    def test_optional_logs_call_count(self):
        """(선택) 로그에 API 호출 횟수를 출력한다 (권장 구현)"""
        _code, output, _fake = self.run_cli(['commit'])
        self.assertRegex(output, r'(호출|call).*1|1.*(호출|call)')


class PrFlowTest(FlowTestCase):

    def test_pr_prints_title_and_body(self):
        """pr: 'PR Title' 다음 제목, 'PR Body' 와 세 섹션이 출력된다"""
        code, output, fake = self.run_cli(['pr'])
        self.assertEqual(code, 0, output)
        self.assertEqual(line_after(output, 'PR Title'),
                         FAKE_PR_TEXT.splitlines()[0])
        for section in ('## Why', '## What', '## How to Test'):
            self.assertIn(section, output)
        self.assertEqual(fake.call_count, 1)

    def test_pr_shows_branch(self):
        """pr: 현재 브랜치 이름을 출력하고 AI 요청에도 넣는다"""
        _code, output, fake = self.run_cli(['pr'])
        self.assertIn('feature/add-search', output)
        self.assertIn('feature/add-search', fake.sent_text())

    def test_pr_sections_have_bullets(self):
        """pr: 출력된 각 섹션 아래에 불릿이 1개 이상 있다"""
        _code, output, _fake = self.run_cli(['pr'])
        body = output.split('PR Body', 1)[1]
        for section, next_section in (('## Why', '## What'),
                                      ('## What', '## How to Test'),
                                      ('## How to Test', None)):
            part = body.split(section, 1)[1]
            if next_section:
                part = part.split(next_section, 1)[0]
            bullets = [line for line in part.splitlines()
                       if line.strip().startswith(('- ', '* '))]
            self.assertTrue(bullets, f'{section} 아래 불릿이 없습니다.')

    def test_long_pr_title_is_fixed(self):
        """AI 가 80자 넘는 PR 제목을 줘도 최종 출력 제목은 80자 이하"""
        long_title = FAKE_LONG_TITLE_TEXT.splitlines()[0]
        text = long_title + '\n' + FAKE_PR_TEXT.split('\n', 1)[1]
        fake = FakeTransport(text=text)
        code, output, _fake = self.run_cli(['pr'], transport=fake)
        self.assertEqual(code, 0, output)
        title = line_after(output, 'PR Title')
        self.assertLessEqual(len(title), config.PR_TITLE_MAX)


class ErrorFlowTest(FlowTestCase):

    def test_no_changes(self):
        """변경 없음: '변경 사항이 없습니다' 출력, AI 호출 0회, 종료 코드 0"""
        code, output, fake = self.run_cli(['commit'], scenario='clean')
        self.assertIn('변경 사항이 없습니다', output)
        self.assertEqual(fake.call_count, 0)
        self.assertEqual(code, 0)

    def test_no_changes_pr(self):
        """pr 도 변경이 없으면 AI 를 부르지 않는다"""
        _code, output, fake = self.run_cli(['pr'], scenario='clean')
        self.assertIn('변경 사항이 없습니다', output)
        self.assertEqual(fake.call_count, 0)

    def test_missing_api_key(self):
        """API Key 없음: [ERROR] + AI_API_KEY 안내, AI 호출 0회, 종료 코드 1"""
        code, output, fake = self.run_cli(['commit'], key=False)
        self.assertIn('[ERROR]', output)
        self.assertIn('AI_API_KEY', output)
        self.assertEqual(fake.call_count, 0)
        self.assertNotEqual(code, 0)

    def test_not_a_git_repository(self):
        """Git 저장소가 아닌 폴더: [ERROR] 출력, 0 이 아닌 종료 코드"""
        folder = str(self.make_temp_dir())
        code, output, fake = self.run_cli(['commit'], repo=folder)
        self.assertIn('[ERROR]', output)
        self.assertNotEqual(code, 0)
        self.assertEqual(fake.call_count, 0)

    def test_api_failure_shows_reason(self):
        """API 실패: [ERROR] 와 오류 원인(HTTP 401)이 출력된다"""
        from ai_gitgen.ai_client import AIClientError
        error = AIClientError('AI API 요청 실패 (HTTP 401): invalid x-api-key')
        code, output, _fake = self.run_cli(
            ['commit'], transport=FakeTransport(error=error))
        self.assertIn('[ERROR]', output)
        self.assertIn('401', output)
        self.assertNotEqual(code, 0)

    def test_invalid_option_stops_before_ai(self):
        """잘못된 옵션(--temperature 5): 오류 안내, AI 호출 0회"""
        code, output, fake = self.run_cli(['commit', '--temperature', '5'])
        self.assertIn('temperature', output)
        self.assertNotEqual(code, 0)
        self.assertEqual(fake.call_count, 0)


class SafeModeFlowTest(FlowTestCase):

    def test_safe_mode_hides_secrets(self):
        """--safe-mode: 가짜 키·이메일이 AI 요청에 들어가지 않는다"""
        _code, _output, fake = self.run_cli(['commit', '--safe-mode'],
                                            scenario='secret')
        sent = fake.sent_text()
        self.assertNotIn('sk-fake-practice', sent)
        self.assertNotIn('admin@example.com', sent)

    def test_without_safe_mode_diff_is_sent_as_is(self):
        """--safe-mode 가 없으면 diff 가 그대로 간다 (차이 확인용)"""
        _code, _output, fake = self.run_cli(['commit'], scenario='secret')
        self.assertIn('sk-fake-practice', fake.sent_text())

    def test_safe_mode_limits_large_diff(self):
        """--safe-mode: 큰 diff(15파일)는 최대 10파일만 보낸다"""
        _code, _output, fake = self.run_cli(['commit', '--safe-mode'],
                                            scenario='large')
        prompt = json.dumps(fake.calls[0]['body'], ensure_ascii=False)
        self.assertLessEqual(prompt.count('diff --git '), 10)


class DryRunFlowTest(FlowTestCase):

    def test_optional_dry_run_does_not_call_ai(self):
        """(선택) --dry-run: 프롬프트만 보여 주고 AI 는 부르지 않는다"""
        code, output, fake = self.run_cli(['commit', '--dry-run'])
        self.assertEqual(code, 0)
        self.assertEqual(fake.call_count, 0)
        self.assertIn('todo_app/search.py', output)


if __name__ == '__main__':
    unittest.main()
