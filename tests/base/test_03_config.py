"""기본 환경 테스트 3 — config.py 기본값이 공식 규칙과 맞는지 확인."""

import unittest

from ai_gitgen import config


class ConfigTest(unittest.TestCase):

    def test_api_key_env_name(self):
        """API Key 환경변수 이름은 AI_API_KEY 다 (공식 예시와 같음)"""
        self.assertEqual(config.API_KEY_ENV_NAME, 'AI_API_KEY')

    def test_length_rules(self):
        """길이 규칙: 커밋 50(권장)/72(최대), PR 제목 80"""
        self.assertEqual(config.COMMIT_TITLE_RECOMMENDED, 50)
        self.assertEqual(config.COMMIT_TITLE_MAX, 72)
        self.assertEqual(config.PR_TITLE_MAX, 80)

    def test_pr_sections(self):
        """PR 본문 섹션은 Why / What / How to Test 다"""
        self.assertEqual(tuple(config.PR_SECTIONS),
                         ('Why', 'What', 'How to Test'))

    def test_defaults_are_in_range(self):
        """temperature / max_tokens 기본값이 허용 범위 안에 있다"""
        self.assertLessEqual(config.TEMPERATURE_MIN,
                             config.DEFAULT_TEMPERATURE)
        self.assertLessEqual(config.DEFAULT_TEMPERATURE,
                             config.TEMPERATURE_MAX)
        self.assertLessEqual(config.MAX_TOKENS_MIN,
                             config.DEFAULT_MAX_TOKENS)
        self.assertLessEqual(config.DEFAULT_MAX_TOKENS,
                             config.MAX_TOKENS_LIMIT)
        self.assertIsInstance(config.DEFAULT_MAX_TOKENS, int)
        self.assertTrue(config.DEFAULT_MODEL.strip())

    def test_provider_settings(self):
        """기본 제공자 설정에 https 주소가 있다"""
        self.assertIn(config.DEFAULT_PROVIDER, config.PROVIDERS)
        for name, settings in config.PROVIDERS.items():
            with self.subTest(provider=name):
                self.assertTrue(settings['url'].startswith('https://'))

    def test_cost_and_safety_limits(self):
        """호출 횟수(1~2회)와 safe-mode 전송 제한(10파일/200줄) 기본값"""
        self.assertIn(config.MAX_API_CALLS_PER_RUN, (1, 2))
        self.assertEqual(config.SAFE_MODE_MAX_FILES, 10)
        self.assertEqual(config.SAFE_MODE_MAX_LINES, 200)
        self.assertGreater(config.REQUEST_TIMEOUT_SECONDS, 0)


if __name__ == '__main__':
    unittest.main()
