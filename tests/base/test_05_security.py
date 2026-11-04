"""기본 환경 테스트 5 — 보안 기본기 (비밀키가 파일에 없는지).

[중요] 이 테스트는 앞으로도 계속 통과해야 한다.
실수로 진짜 API Key 를 파일에 붙여 넣으면 이 테스트가 실패해서 알려 준다.
연습용 가짜 값에는 반드시 fake / test / example / dummy / demo 중
하나가 들어가게 만든다.
"""

import re
import unittest

from tests.helpers import PROJECT_ROOT

SKIP_DIRS = {'.git', 'practice_repo', '__pycache__', '.venv', 'venv'}
TEXT_SUFFIXES = {'.py', '.md', '.txt', '.diff', '.json', '.html', '.yml',
                 '.yaml', '.toml', '.cfg', '.ini', '.sh', ''}

# 실제 서비스 키에서 흔히 보이는 모양들
KEY_PATTERNS = [
    re.compile(r'sk-[A-Za-z0-9_\-]{16,}'),            # sk-... 형태
    re.compile(r'AKIA[0-9A-Z]{16}'),                  # AWS
    re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),        # GitHub 토큰
    re.compile(r'AIza[0-9A-Za-z_\-]{35}'),            # Google
    re.compile(r'xox[baprs]-[A-Za-z0-9\-]{10,}'),     # Slack
]
FAKE_WORDS = ('fake', 'test', 'example', 'dummy', 'demo', 'your', 'xxxx')


def iter_project_files():
    for path in PROJECT_ROOT.rglob('*'):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


class SecurityBaselineTest(unittest.TestCase):

    def test_no_real_looking_keys_in_files(self):
        """프로젝트 파일에 진짜처럼 보이는 API Key 가 없다"""
        problems = []
        for path in iter_project_files():
            text = path.read_text(encoding='utf-8', errors='ignore')
            for pattern in KEY_PATTERNS:
                for match in pattern.finditer(text):
                    value = match.group(0).lower()
                    if not any(word in value for word in FAKE_WORDS):
                        relative = path.relative_to(PROJECT_ROOT)
                        problems.append(f'{relative}: {match.group(0)[:8]}…')
        self.assertEqual(
            problems, [],
            '키처럼 보이는 값이 있습니다. 진짜 키라면 즉시 지우고, '
            '제공자 사이트에서 키를 폐기(재발급)하세요.')

    def test_gitignore_protects_secrets(self):
        """.gitignore 가 .env 와 연습 저장소를 커밋에서 제외한다"""
        gitignore = (PROJECT_ROOT / '.gitignore').read_text(encoding='utf-8')
        self.assertIn('.env', gitignore)
        self.assertIn('practice_repo/', gitignore)

    def test_no_env_files_in_project(self):
        """프로젝트 폴더에 .env 파일이 없다"""
        found = [p.name for p in PROJECT_ROOT.glob('.env*')]
        self.assertEqual(found, [], '.env 파일 대신 환경변수를 사용하세요.')

    def test_api_key_read_only_from_environment(self):
        """ai_gitgen 코드에 API Key 를 직접 대입한 줄이 없다"""
        pattern = re.compile(
            r'''(?i)(api_?key|secret|token)\s*=\s*['"]([^'"\s]{8,})['"]''')
        problems = []
        for path in (PROJECT_ROOT / 'ai_gitgen').glob('*.py'):
            for number, line in enumerate(
                    path.read_text(encoding='utf-8').splitlines(), 1):
                match = pattern.search(line)
                if match and not any(word in match.group(2).lower()
                                     for word in FAKE_WORDS):
                    problems.append(f'{path.name}:{number}: {line.strip()}')
        self.assertEqual(problems, [], 'API Key 는 os.environ 으로만 읽어야 합니다.')


if __name__ == '__main__':
    unittest.main()
