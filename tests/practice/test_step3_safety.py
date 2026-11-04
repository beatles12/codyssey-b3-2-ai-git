"""Step 3 연습 테스트 — 안전 모드: 마스킹·전송 제한 (ai_gitgen/safety.py)

실행: python -m learning_kit.practice 3
"""

import unittest

from ai_gitgen import safety
from tests.helpers import PracticeTestCase


def make_big_diff(files=15, lines_per_file=30):
    parts = []
    for number in range(files):
        parts.append(f'diff --git a/f{number}.py b/f{number}.py\n')
        parts.append(f'--- a/f{number}.py\n+++ b/f{number}.py\n')
        parts.extend(f'+line {index}\n' for index in range(lines_per_file))
    return ''.join(parts)


class MaskTest(PracticeTestCase):

    def setUp(self):
        super().setUp()
        self.diff = self.read_data('git_diff_with_secrets.diff')

    def test_api_key_is_masked(self):
        """'sk-' 로 시작하는 API Key 모양 문자열이 사라진다"""
        masked = safety.mask_sensitive('token: sk-fake-abcdefghijklmnop1234')
        self.assertNotIn('sk-fake-abcdefghijklmnop1234', masked)
        self.assertIn(safety.MASK_TEXT, masked)

    def test_assigned_secret_values_are_masked(self):
        """API_KEY = "..." / DB_PASSWORD = "..." 같은 대입 값이 사라진다"""
        masked = safety.mask_sensitive(
            'API_KEY = "my-fake-key-value-1"\n'
            'DB_PASSWORD = "fake-password-1234"\n'
            "secret: 'fake-secret-999'\n")
        for value in ('my-fake-key-value-1', 'fake-password-1234',
                      'fake-secret-999'):
            with self.subTest(value=value):
                self.assertNotIn(value, masked)

    def test_email_is_masked(self):
        """이메일 주소가 사라진다"""
        masked = safety.mask_sensitive('contact: kim.dev@example.com 입니다')
        self.assertNotIn('kim.dev@example.com', masked)
        self.assertIn(safety.MASK_TEXT, masked)
        self.assertIn('입니다', masked)

    def test_sample_diff_has_no_secrets_after_masking(self):
        """git_diff_with_secrets.diff 의 가짜 키·이메일·비밀번호가 모두 사라진다"""
        masked = safety.mask_sensitive(self.diff)
        for secret in ('sk-fake-practice-0000000000abcdef',
                       'admin@example.com', 'fake-password-1234'):
            with self.subTest(secret=secret):
                self.assertNotIn(secret, masked)

    def test_normal_code_is_unchanged(self):
        """민감정보가 아닌 코드는 그대로 남는다"""
        text = ("def add_todo(title):\n"
                "    TODOS.append({'title': title})\n"
                "APP_NAME = 'Todo App'\n")
        self.assertEqual(safety.mask_sensitive(text), text)

    def test_diff_structure_is_kept(self):
        """마스킹 후에도 diff 의 줄 수와 파일 머리줄은 그대로다"""
        masked = safety.mask_sensitive(self.diff)
        self.assertEqual(len(masked.splitlines()),
                         len(self.diff.splitlines()))
        self.assertIn('diff --git a/todo_app/settings.py', masked)

    def test_optional_phone_number_is_masked(self):
        """(선택) 휴대전화 번호 010-1234-5678 도 가린다"""
        masked = safety.mask_sensitive('SUPPORT_PHONE = "010-1234-5678"')
        self.assertNotIn('010-1234-5678', masked)


class LimitDiffTest(PracticeTestCase):

    def test_small_diff_is_unchanged(self):
        """제한보다 작은 diff 는 그대로 돌려준다"""
        diff = self.read_data('git_diff_sample.diff')
        self.assertEqual(safety.limit_diff(diff), diff)

    def test_limits_number_of_files(self):
        """파일 15개 diff -> 최대 10개 파일만 남는다"""
        result = safety.limit_diff(make_big_diff(files=15, lines_per_file=3))
        self.assertLessEqual(result.count('diff --git '), 10)
        self.assertIn('diff --git a/f0.py', result)

    def test_limits_number_of_lines(self):
        """300줄이 넘는 diff -> 200줄 + 안내 1줄 이하로 줄어든다"""
        big = make_big_diff(files=5, lines_per_file=80)
        result = safety.limit_diff(big)
        self.assertLessEqual(len(result.splitlines()), 201)
        self.assertTrue(big.startswith(result.splitlines()[0]))

    def test_custom_limits(self):
        """max_files / max_lines 값을 바꿔 줄 수 있다"""
        result = safety.limit_diff(make_big_diff(), max_files=2,
                                   max_lines=20)
        self.assertLessEqual(result.count('diff --git '), 2)
        self.assertLessEqual(len(result.splitlines()), 21)

    def test_optional_notice_when_truncated(self):
        """(선택) 잘라 냈으면 마지막에 '생략' 같은 안내가 붙는다"""
        result = safety.limit_diff(make_big_diff())
        last = result.splitlines()[-1]
        self.assertTrue(any(word in last for word in
                            ('생략', 'truncated', 'omitted', '...')))


class ApplySafeModeTest(PracticeTestCase):

    def test_disabled_returns_original(self):
        """enabled=False 면 원본을 그대로 돌려준다"""
        diff = self.read_data('git_diff_with_secrets.diff')
        self.assertEqual(safety.apply_safe_mode(diff, False), diff)

    def test_enabled_masks_and_limits(self):
        """enabled=True 면 마스킹과 전송 제한이 모두 적용된다"""
        diff = self.read_data('git_diff_with_secrets.diff') + make_big_diff()
        result = safety.apply_safe_mode(diff, True)
        self.assertNotIn('sk-fake-practice', result)
        self.assertLessEqual(len(result.splitlines()), 201)


if __name__ == '__main__':
    unittest.main()
