"""Step 1 연습 테스트 — CLI 옵션 만들기·입력값 검사 (ai_gitgen/cli.py)

실행: python -m learning_kit.practice 1
"""

import unittest

from ai_gitgen import cli, config
from tests.helpers import PracticeTestCase


class BuildParserTest(PracticeTestCase):

    def parse_argv(self, argv):
        return cli.build_parser().parse_args(argv)

    def test_commit_command_with_defaults(self):
        """commit 명령만 주면 모든 옵션이 config 기본값이다"""
        args = self.parse_argv(['commit'])
        self.assertEqual(args.command, 'commit')
        self.assertEqual(args.model, config.DEFAULT_MODEL)
        self.assertEqual(args.temperature, config.DEFAULT_TEMPERATURE)
        self.assertEqual(args.max_tokens, config.DEFAULT_MAX_TOKENS)
        self.assertFalse(args.safe_mode)

    def test_pr_command_with_all_options(self):
        """pr 명령 뒤에 --model --temperature --max-tokens --safe-mode 를 쓸 수 있다"""
        args = self.parse_argv(['pr', '--model', 'my-model', '--temperature',
                                '0.7', '--max-tokens', '300', '--safe-mode'])
        self.assertEqual(args.command, 'pr')
        self.assertEqual(args.model, 'my-model')
        self.assertEqual(args.temperature, 0.7)
        self.assertEqual(args.max_tokens, 300)
        self.assertTrue(args.safe_mode)

    def test_types_are_converted(self):
        """temperature 는 float, max_tokens 는 int 로 바뀐다"""
        args = self.parse_argv(['commit', '--temperature', '1', '--max-tokens',
                                '50'])
        self.assertIsInstance(args.temperature, float)
        self.assertIsInstance(args.max_tokens, int)

    def test_missing_command_exits(self):
        """하위 명령(commit/pr) 없이 실행하면 SystemExit 이 발생한다"""
        result, _output = self.capture(self.parse_argv, [])
        self.assertNotEqual(result, 0)
        self.assertIsNotNone(result)

    def test_unknown_command_exits(self):
        """모르는 명령(push)은 SystemExit 으로 거부한다"""
        result, _output = self.capture(self.parse_argv, ['push'])
        self.assertNotIn(result, (0, None))

    def test_non_number_max_tokens_exits(self):
        """--max-tokens abc 처럼 숫자가 아니면 SystemExit 이 발생한다"""
        result, _output = self.capture(self.parse_argv,
                                       ['commit', '--max-tokens', 'abc'])
        self.assertNotIn(result, (0, None))

    def test_optional_dry_run_flag(self):
        """(선택) --dry-run 옵션이 있고 기본값은 False 다"""
        self.assertFalse(self.parse_argv(['commit']).dry_run)
        self.assertTrue(self.parse_argv(['commit', '--dry-run']).dry_run)


class ValidateOptionsTest(PracticeTestCase):

    def problems_for(self, argv):
        return cli.validate_options(cli.build_parser().parse_args(argv))

    def test_default_options_are_valid(self):
        """기본값만 쓰면 문제 목록이 비어 있다 ([])"""
        self.assertEqual(self.problems_for(['commit']), [])

    def test_boundary_values_are_valid(self):
        """경계값 temperature 0.0 / 1.0, max_tokens 1 은 허용한다"""
        for argv in (['commit', '--temperature', '0.0'],
                     ['pr', '--temperature', '1.0'],
                     ['commit', '--max-tokens', '1']):
            self.assertEqual(self.problems_for(argv), [], argv)

    def test_temperature_out_of_range(self):
        """temperature 1.5 나 -0.1 은 'temperature' 가 들어간 문제 메시지"""
        for value in ('1.5', '-0.1'):
            with self.subTest(temperature=value):
                argv = ['commit', '--temperature', value]
                problems = self.problems_for(argv)
                self.assertTrue(problems, '문제 목록이 비어 있습니다.')
                self.assertTrue(any('temperature' in p for p in problems))

    def test_max_tokens_out_of_range(self):
        """max_tokens 0 이나 상한 초과는 'max' 가 들어간 문제 메시지"""
        too_big = str(config.MAX_TOKENS_LIMIT + 1)
        for value in ('0', too_big):
            with self.subTest(max_tokens=value):
                argv = ['commit', '--max-tokens', value]
                problems = self.problems_for(argv)
                self.assertTrue(problems, '문제 목록이 비어 있습니다.')
                self.assertTrue(any('max' in p.lower() for p in problems))

    def test_empty_model(self):
        """--model '' (빈 문자열)은 'model' 이 들어간 문제 메시지"""
        problems = self.problems_for(['commit', '--model', ''])
        self.assertTrue(any('model' in p.lower() for p in problems))

    def test_returns_list_of_strings(self):
        """반환값은 문자열들의 list 다"""
        problems = self.problems_for(['commit', '--temperature', '9'])
        self.assertIsInstance(problems, list)
        self.assertTrue(all(isinstance(p, str) for p in problems))


if __name__ == '__main__':
    unittest.main()
