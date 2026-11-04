"""Step 4 연습 테스트 — 프롬프트 만들기 (ai_gitgen/prompt_builder.py)

실행: python -m learning_kit.practice 4

테스트는 "반드시 들어가야 할 정보"만 확인한다. 문장 표현은 자유다.
"""

import os
import unittest

from ai_gitgen import prompt_builder as pb
from tests.helpers import PracticeTestCase

FILES = [
    {'code': 'M', 'path': 'README.md'},
    {'code': 'M', 'path': 'todo_app/app.py'},
    {'code': 'A', 'path': 'todo_app/search.py'},
]


class FileListTest(PracticeTestCase):

    def test_all_paths_and_codes(self):
        """모든 경로와 상태 코드가 들어간 여러 줄 문자열"""
        text = pb.format_file_list(FILES)
        self.assertIsInstance(text, str)
        for item in FILES:
            self.assertIn(item['path'], text)
        self.assertIn('A', text)
        self.assertGreaterEqual(len(text.strip().splitlines()), 3)

    def test_empty_list(self):
        """빈 목록이어도 오류 없이 빈칸이 아닌 안내 문자열"""
        text = pb.format_file_list([])
        self.assertIsInstance(text, str)
        self.assertTrue(text.strip())


class CommitPromptTest(PracticeTestCase):

    def setUp(self):
        super().setUp()
        self.diff = self.read_data('git_diff_sample.diff')
        self.prompt = pb.build_commit_prompt(FILES, self.diff)

    def test_contains_paths_and_diff(self):
        """변경 파일 경로와 diff 내용이 모두 들어 있다"""
        for item in FILES:
            self.assertIn(item['path'], self.prompt)
        self.assertIn(self.diff.strip(), self.prompt)

    def test_mentions_title_length_rule(self):
        """커밋 제목 길이 규칙 숫자(50 또는 72)가 들어 있다"""
        self.assertTrue('50' in self.prompt or '72' in self.prompt)

    def test_is_deterministic(self):
        """같은 입력이면 항상 같은 프롬프트 (재현성)"""
        self.assertEqual(self.prompt, pb.build_commit_prompt(FILES, self.diff))

    def test_works_with_empty_diff(self):
        """diff 가 비어 있어도(새 파일만 있는 경우) 오류 없이 만든다"""
        prompt = pb.build_commit_prompt([{'code': '??', 'path': 'NOTES.md'}],
                                        '')
        self.assertIn('NOTES.md', prompt)

    def test_never_contains_api_key(self):
        """환경변수의 API Key 값은 프롬프트에 절대 들어가지 않는다"""
        os.environ['AI_API_KEY'] = 'fake-key-must-not-leak'
        prompt = pb.build_commit_prompt(FILES, self.diff)
        self.assertNotIn('fake-key-must-not-leak', prompt)

    def test_optional_language_instruction(self):
        """(선택) 출력 언어(한국어)를 지정한다"""
        self.assertTrue('한국어' in self.prompt
                        or 'korean' in self.prompt.lower())


class PrPromptTest(PracticeTestCase):

    def setUp(self):
        super().setUp()
        self.diff = self.read_data('git_diff_sample.diff')
        self.prompt = pb.build_pr_prompt(FILES, self.diff,
                                         'feature/add-search')

    def test_contains_context(self):
        """파일 경로, diff, 브랜치 이름이 모두 들어 있다"""
        for item in FILES:
            self.assertIn(item['path'], self.prompt)
        self.assertIn(self.diff.strip(), self.prompt)
        self.assertIn('feature/add-search', self.prompt)

    def test_contains_sections(self):
        """PR 본문 섹션 이름 Why / What / How to Test 가 들어 있다"""
        for section in ('Why', 'What', 'How to Test'):
            self.assertIn(section, self.prompt)

    def test_mentions_pr_title_limit(self):
        """PR 제목 최대 길이 숫자 80 이 들어 있다"""
        self.assertIn('80', self.prompt)

    def test_commit_and_pr_prompts_differ(self):
        """커밋용과 PR용 프롬프트는 서로 다르다 (용도에 맞는 지시)"""
        self.assertNotEqual(self.prompt,
                            pb.build_commit_prompt(FILES, self.diff))


if __name__ == '__main__':
    unittest.main()
