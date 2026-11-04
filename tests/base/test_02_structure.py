"""기본 환경 테스트 2 — 폴더 구조와 함수 약속(이름·매개변수).

연습 테스트는 여기 적힌 함수 이름과 매개변수 이름을 기준으로 작성되어 있다.
함수 이름이나 매개변수 이름을 바꾸면 이 테스트가 먼저 알려 준다.
(본문 구현 여부는 검사하지 않는다.)
"""

import importlib
import inspect
import unittest

from tests.helpers import PROJECT_ROOT

REQUIRED_FILES = [
    'START_HERE.md',
    'README.md',
    'main.py',
    'requirements.txt',
    '.gitignore',
    'ai_gitgen/__init__.py',
    'ai_gitgen/config.py',
    'ai_gitgen/cli.py',
    'ai_gitgen/git_collector.py',
    'ai_gitgen/safety.py',
    'ai_gitgen/prompt_builder.py',
    'ai_gitgen/ai_client.py',
    'ai_gitgen/formatter.py',
    'learning_kit/practice.py',
    'learning_kit/practice_repo.py',
    'learning_kit/fake_ai.py',
    'learning_kit/demo.py',
    'learning_kit/check_env.py',
    'docs/B3-2_STUDY_GUIDE.html',
    'docs/PRACTICE_STEPS.md',
    'docs/REQUIREMENTS_ANALYSIS.md',
    'docs/templates/README_TEMPLATE.md',
    'docs/templates/MY_ANSWERS.md',
    'practice_data/README.md',
    'practice_data/git_status_sample.txt',
    'practice_data/git_diff_sample.diff',
    'practice_data/git_diff_with_secrets.diff',
    'practice_data/git_log_sample.txt',
]

# 모듈 이름 -> {함수 이름: 앞쪽 매개변수 이름 목록}
CONTRACTS = {
    'ai_gitgen.cli': {
        'log': ['level', 'message'],
        'build_parser': [],
        'validate_options': ['args'],
        'run_commit': ['args', 'cwd', 'transport'],
        'run_pr': ['args', 'cwd', 'transport'],
        'main': ['argv', 'cwd', 'transport'],
    },
    'ai_gitgen.git_collector': {
        'run_git': ['args', 'cwd'],
        'is_git_repository': ['cwd'],
        'parse_status_output': ['status_text'],
        'get_changed_files': ['cwd'],
        'get_diff': ['cwd'],
        'count_diff_lines': ['diff_text'],
        'get_current_branch': ['cwd'],
    },
    'ai_gitgen.safety': {
        'mask_sensitive': ['text'],
        'limit_diff': ['diff_text', 'max_files', 'max_lines'],
        'apply_safe_mode': ['diff_text', 'enabled'],
    },
    'ai_gitgen.prompt_builder': {
        'format_file_list': ['changed_files'],
        'build_commit_prompt': ['changed_files', 'diff_text'],
        'build_pr_prompt': ['changed_files', 'diff_text', 'branch_name'],
    },
    'ai_gitgen.ai_client': {
        'get_api_key': ['env_name'],
        'build_headers': ['api_key', 'provider'],
        'build_request_body': ['prompt', 'model', 'temperature',
                               'max_tokens', 'provider'],
        'extract_text': ['response_data', 'provider'],
        'send_http_request': ['url', 'headers', 'body', 'timeout'],
        'call_ai_api': ['prompt', 'model', 'temperature', 'max_tokens',
                        'provider', 'api_key', 'transport'],
    },
    'ai_gitgen.formatter': {
        'split_title_body': ['text'],
        'shorten_title': ['title', 'max_length'],
        'validate_commit_message': ['message', 'changed_paths'],
        'validate_pr_title': ['title'],
        'validate_pr_body': ['body'],
        'format_commit_output': ['message'],
        'format_pr_output': ['title', 'body'],
    },
}

EXCEPTIONS = {
    'ai_gitgen.git_collector': ['GitCommandError'],
    'ai_gitgen.ai_client': ['AIClientError', 'MissingApiKeyError'],
}


class StructureTest(unittest.TestCase):

    def test_required_files_exist(self):
        """필요한 파일과 폴더가 모두 있다"""
        missing = [name for name in REQUIRED_FILES
                   if not (PROJECT_ROOT / name).exists()]
        self.assertEqual(missing, [], f'없는 파일: {missing}')

    def test_modules_import(self):
        """ai_gitgen 의 모든 모듈을 import 할 수 있다 (문법 오류 없음)"""
        for module_name in CONTRACTS:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)

    def test_function_contracts(self):
        """함수 이름과 매개변수 이름이 실습 약속과 같다"""
        for module_name, functions in CONTRACTS.items():
            module = importlib.import_module(module_name)
            for func_name, expected in functions.items():
                with self.subTest(function=f'{module_name}.{func_name}'):
                    func = getattr(module, func_name, None)
                    self.assertTrue(callable(func),
                                    f'{func_name} 함수가 없습니다.')
                    params = list(inspect.signature(func).parameters)
                    self.assertEqual(
                        params[:len(expected)], expected,
                        f'{func_name} 의 매개변수는 {expected} 로 '
                        f'시작해야 합니다. (지금: {params})')

    def test_exception_classes(self):
        """예외 클래스가 준비되어 있다"""
        for module_name, names in EXCEPTIONS.items():
            module = importlib.import_module(module_name)
            for name in names:
                with self.subTest(exception=name):
                    cls = getattr(module, name, None)
                    self.assertTrue(inspect.isclass(cls))
                    self.assertTrue(issubclass(cls, Exception))
        from ai_gitgen.ai_client import AIClientError, MissingApiKeyError
        self.assertTrue(issubclass(MissingApiKeyError, AIClientError))

    def test_safety_constants(self):
        """safety.py 의 MASK_TEXT 와 SENSITIVE_PATTERNS 가 있다"""
        from ai_gitgen import safety
        self.assertIsInstance(safety.MASK_TEXT, str)
        self.assertIsInstance(safety.SENSITIVE_PATTERNS, list)


if __name__ == '__main__':
    unittest.main()
