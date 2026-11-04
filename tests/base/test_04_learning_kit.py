"""기본 환경 테스트 4 — 연습 도구(연습 저장소, 가짜 AI, 연습 데이터)."""

import json
import subprocess
import unittest

from learning_kit import fake_ai
from learning_kit.practice_repo import SCENARIOS, remove_practice_repo
from tests.helpers import PracticeTestCase


def git_output(repo, *args):
    """learning_kit 과 별개로 git 을 직접 실행한다. (도구 자체 검증용)"""
    result = subprocess.run(['git', *args], cwd=repo, capture_output=True,
                            text=True, encoding='utf-8')
    return result.stdout


class PracticeRepoTest(PracticeTestCase):

    def test_feature_scenario(self):
        """feature 시나리오: staged 2개 + unstaged 1개, 브랜치 feature/add-search"""
        repo = self.make_repo('feature')
        status = git_output(repo, 'status', '--porcelain')
        self.assertIn('M  README.md', status)
        self.assertIn(' M todo_app/app.py', status)
        self.assertIn('A  todo_app/search.py', status)
        self.assertEqual(git_output(repo, 'branch', '--show-current').strip(),
                         'feature/add-search')
        self.assertIn('search_todos', git_output(repo, 'diff', '--cached'))
        self.assertIn('complete_todo', git_output(repo, 'diff'))

    def test_clean_scenario(self):
        """clean 시나리오: 변경 사항이 하나도 없다"""
        repo = self.make_repo('clean')
        self.assertEqual(git_output(repo, 'status', '--porcelain'), '')

    def test_secret_scenario_contains_fake_secrets(self):
        """secret 시나리오: diff 에 가짜 키·이메일이 들어 있다"""
        repo = self.make_repo('secret')
        diff = git_output(repo, 'diff')
        self.assertIn('sk-fake-practice', diff)
        self.assertIn('admin@example.com', diff)

    def test_large_scenario_is_large(self):
        """large 시나리오: 파일 15개, 300줄 이상"""
        repo = self.make_repo('large')
        diff = git_output(repo, 'diff', '--cached')
        self.assertEqual(diff.count('diff --git '), 15)
        self.assertGreater(len(diff.splitlines()), 300)

    def test_all_scenarios_can_be_created(self):
        """모든 시나리오를 오류 없이 만들 수 있다"""
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario):
                repo = self.make_repo(scenario)
                self.assertIn('true', git_output(
                    repo, 'rev-parse', '--is-inside-work-tree'))

    def test_never_removes_other_folders(self):
        """연습 저장소가 아닌 폴더는 지우지 않는다"""
        folder = self.make_temp_dir() / 'important'
        folder.mkdir()
        (folder / 'keep.txt').write_text('지우면 안 됨', encoding='utf-8')
        with self.assertRaises(RuntimeError):
            remove_practice_repo(folder)
        self.assertTrue((folder / 'keep.txt').exists())


class FakeAITest(unittest.TestCase):

    def test_records_calls_and_returns_anthropic_shape(self):
        """가짜 AI 는 호출을 기록하고 Anthropic 응답 모양을 돌려준다"""
        fake = fake_ai.FakeTransport()
        data = fake('https://api.anthropic.com/v1/messages', {'x': '1'},
                    {'messages': [{'role': 'user', 'content': '커밋'}]}, 5)
        self.assertEqual(fake.call_count, 1)
        self.assertEqual(data['content'][-1]['type'], 'text')
        self.assertEqual(data['content'][-1]['text'],
                         fake_ai.FAKE_COMMIT_TEXT)

    def test_openai_shape_and_pr_text(self):
        """openai 주소면 choices 모양, 프롬프트에 How to Test 가 있으면 PR 글"""
        fake = fake_ai.FakeTransport()
        data = fake('https://api.openai.com/v1/chat/completions', {},
                    {'messages': [{'role': 'user',
                                   'content': 'Why What How to Test'}]}, 5)
        self.assertEqual(data['choices'][0]['message']['content'],
                         fake_ai.FAKE_PR_TEXT)

    def test_error_injection(self):
        """error 를 주면 그 예외를 발생시킨다"""
        fake = fake_ai.FakeTransport(error=ValueError('boom'))
        with self.assertRaises(ValueError):
            fake('u', {}, {}, 1)
        self.assertEqual(fake.call_count, 1)

    def test_fake_texts_follow_rules(self):
        """가짜 정상 응답은 공식 형식 규칙을 지킨다"""
        commit_title = fake_ai.FAKE_COMMIT_TEXT.splitlines()[0]
        self.assertLessEqual(len(commit_title), 50)
        for section in ('## Why', '## What', '## How to Test'):
            self.assertIn(section, fake_ai.FAKE_PR_TEXT)
        long_title = fake_ai.FAKE_LONG_TITLE_TEXT.splitlines()[0]
        self.assertGreater(len(long_title), 80)


class PracticeDataTest(PracticeTestCase):

    def test_sample_files_are_readable(self):
        """연습 데이터 파일을 읽을 수 있고 내용이 예상과 같다"""
        self.assertIn(' M todo_app/app.py',
                      self.read_data('git_status_sample.txt'))
        self.assertEqual(
            self.read_data('git_diff_sample.diff').count('diff --git '), 3)
        self.assertIn('sk-fake-practice',
                      self.read_data('git_diff_with_secrets.diff'))
        self.assertIn('commit ', self.read_data('git_log_sample.txt'))

    def test_api_response_samples_are_valid_json(self):
        """api_responses 폴더의 JSON 파일이 모두 올바른 JSON 이다"""
        for name in ('anthropic_commit', 'anthropic_pr',
                     'anthropic_max_tokens', 'openai_commit',
                     'anthropic_error_401', 'anthropic_error_400',
                     'anthropic_error_429'):
            with self.subTest(file=name):
                data = json.loads(self.read_data(
                    f'api_responses/{name}.json'))
                self.assertIsInstance(data, dict)


if __name__ == '__main__':
    unittest.main()
