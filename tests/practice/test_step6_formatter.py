"""Step 6 연습 테스트 — 출력 검증·다듬기 (ai_gitgen/formatter.py)

실행: python -m learning_kit.practice 6
"""

import unittest

from ai_gitgen import formatter as fm
from learning_kit.fake_ai import FAKE_COMMIT_TEXT, FAKE_PR_TEXT
from tests.helpers import PracticeTestCase, has_separator, line_after

PR_TITLE, PR_BODY = FAKE_PR_TEXT.split('\n', 1)
PR_BODY = PR_BODY.strip()


class SplitTitleBodyTest(PracticeTestCase):

    def test_title_and_body(self):
        """첫 줄은 제목, 빈 줄 뒤 나머지는 본문"""
        title, body = fm.split_title_body('feat: 검색 추가\n\n- a\n- b')
        self.assertEqual(title, 'feat: 검색 추가')
        self.assertEqual(body, '- a\n- b')

    def test_leading_blank_lines_and_spaces(self):
        """앞의 빈 줄과 앞뒤 공백을 무시한다"""
        self.assertEqual(fm.split_title_body('\n\n   feat: x   \n'),
                         ('feat: x', ''))

    def test_empty_text(self):
        """빈 글이면 ('', '')"""
        self.assertEqual(fm.split_title_body(''), ('', ''))

    def test_optional_code_fence_is_ignored(self):
        """(선택) AI 가 ``` 로 감싸 답해도 제목을 제대로 찾는다"""
        title, body = fm.split_title_body('```\nfeat: x\n\n- y\n```')
        self.assertEqual(title, 'feat: x')
        self.assertNotIn('```', body)


class ShortenTitleTest(PracticeTestCase):

    def test_short_title_unchanged(self):
        """짧은 제목은 그대로다"""
        self.assertEqual(fm.shorten_title('feat: 검색 추가', 72), 'feat: 검색 추가')

    def test_long_title_is_cut(self):
        """긴 제목은 max_length 글자 이하로 줄고, 앞부분은 유지된다"""
        title = 'feat: ' + 'a' * 100
        result = fm.shorten_title(title, 72)
        self.assertLessEqual(len(result), 72)
        self.assertTrue(result.startswith('feat: aaaa'))

    def test_korean_counts_characters(self):
        """한글도 '글자 수' 기준으로 줄인다 (len 사용)"""
        result = fm.shorten_title('가' * 100, 50)
        self.assertLessEqual(len(result), 50)
        self.assertGreater(len(result), 40)

    def test_exact_length_unchanged(self):
        """정확히 max_length 글자면 그대로다"""
        self.assertEqual(fm.shorten_title('b' * 80, 80), 'b' * 80)


class ValidateCommitTest(PracticeTestCase):

    def test_good_message(self):
        """정상 커밋 메시지는 문제 없음 ([])"""
        self.assertEqual(fm.validate_commit_message(FAKE_COMMIT_TEXT), [])

    def test_title_only_is_ok(self):
        """본문 없이 제목 1줄만 있어도 된다 (본문은 선택)"""
        self.assertEqual(fm.validate_commit_message('fix: 빈 제목 오류 수정'), [])

    def test_empty_message(self):
        """빈 메시지는 문제"""
        self.assertTrue(fm.validate_commit_message(''))

    def test_title_over_72(self):
        """제목이 72자를 넘으면 '72' 가 들어간 문제 메시지"""
        problems = fm.validate_commit_message('feat: ' + 'x' * 80)
        self.assertTrue(problems)
        self.assertTrue(any('72' in p for p in problems))

    def test_title_between_50_and_72_is_allowed(self):
        """51~72자 제목은 권장 초과지만 '문제'는 아니다"""
        self.assertEqual(fm.validate_commit_message('feat: ' + 'x' * 60), [])

    def test_body_needs_bullet_or_file(self):
        """본문이 있으면 불릿 또는 변경 파일 언급이 필요하다"""
        message = 'feat: x\n\n그냥 설명 문장입니다.'
        self.assertTrue(fm.validate_commit_message(message, ['app.py']))
        self.assertEqual(
            fm.validate_commit_message('feat: x\n\napp.py 를 고쳤습니다.',
                                       ['app.py']), [])
        self.assertEqual(fm.validate_commit_message('feat: x\n\n- 검색 추가'), [])


class ValidatePrTest(PracticeTestCase):

    def test_good_title(self):
        """정상 PR 제목은 문제 없음"""
        self.assertEqual(fm.validate_pr_title(PR_TITLE), [])

    def test_bad_titles(self):
        """빈 제목, 80자 초과, 여러 줄 제목은 문제"""
        self.assertTrue(fm.validate_pr_title(''))
        long_problems = fm.validate_pr_title('feat: ' + 'y' * 80)
        self.assertTrue(any('80' in p for p in long_problems))
        self.assertTrue(fm.validate_pr_title('첫 줄\n둘째 줄'))

    def test_good_body(self):
        """Why/What/How to Test + 불릿이 있으면 문제 없음"""
        self.assertEqual(fm.validate_pr_body(PR_BODY), [])

    def test_header_variants_are_accepted(self):
        """'### What', '## Why (변경 배경)' 같은 헤더도 인정한다"""
        body = ('## Why (변경 배경)\n- a\n### What\n* b\n'
                '## How to Test\n- c\n')
        self.assertEqual(fm.validate_pr_body(body), [])

    def test_missing_section(self):
        """How to Test 섹션이 없으면 그 이름이 들어간 문제 메시지"""
        body = '## Why\n- a\n## What\n- b\n'
        problems = fm.validate_pr_body(body)
        self.assertTrue(any('How to Test' in p for p in problems))

    def test_section_without_bullet(self):
        """What 섹션에 불릿이 없으면 'What' 이 들어간 문제 메시지"""
        body = '## Why\n- a\n## What\n설명만 있음\n## How to Test\n- c\n'
        problems = fm.validate_pr_body(body)
        self.assertTrue(problems)
        self.assertTrue(any('What' in p for p in problems))
        self.assertFalse(any('Why' in p for p in problems))


class FormatOutputTest(PracticeTestCase):

    def test_commit_output_layout(self):
        """'Commit Message' 헤더, 다음 줄 제목, 본문, 구분선"""
        output = fm.format_commit_output(FAKE_COMMIT_TEXT)
        self.assertEqual(line_after(output, 'Commit Message'),
                         FAKE_COMMIT_TEXT.splitlines()[0])
        self.assertIn('- README 에 검색 사용 예시 추가', output)
        self.assertTrue(has_separator(output))

    def test_pr_output_layout(self):
        """'PR Title' 헤더 다음 제목, 'PR Body' 헤더 다음 본문, 구분선"""
        output = fm.format_pr_output(PR_TITLE, PR_BODY)
        self.assertEqual(line_after(output, 'PR Title'), PR_TITLE)
        self.assertEqual(line_after(output, 'PR Body'), '## Why')
        for section in ('## What', '## How to Test'):
            self.assertIn(section, output)
        self.assertTrue(has_separator(output))
        self.assertLess(output.index('PR Title'), output.index('PR Body'))


if __name__ == '__main__':
    unittest.main()
