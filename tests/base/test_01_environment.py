"""기본 환경 테스트 1 — Python / Git / 실행 파일."""

import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT


class EnvironmentTest(unittest.TestCase):

    def test_python_version(self):
        """Python 3.10 이상에서 실행 중이다 (공식 개발 환경)"""
        self.assertGreaterEqual(
            sys.version_info[:2], (3, 10),
            'Python 3.10 이상을 설치하세요. (python --version 으로 확인)')

    def test_git_installed(self):
        """git 명령을 실행할 수 있다"""
        try:
            result = subprocess.run(['git', '--version'],
                                    capture_output=True, text=True)
        except FileNotFoundError:
            self.fail('git 을 찾을 수 없습니다. Git 을 설치하세요.')
        self.assertEqual(result.returncode, 0)
        self.assertIn('git version', result.stdout)

    def test_main_py_runs_without_traceback(self):
        """python main.py --help 가 긴 오류(Traceback) 없이 끝난다"""
        result = subprocess.run(
            [sys.executable, 'main.py', '--help'], cwd=PROJECT_ROOT,
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=60)
        self.assertNotIn('Traceback', result.stderr + result.stdout)
        # 0 = 도움말 출력(구현 후), 3 = [TODO] 안내(구현 전)
        self.assertIn(result.returncode, (0, 3))

    def test_utf8_round_trip(self):
        """한글이 UTF-8 로 깨지지 않고 저장·복원된다"""
        text = '커밋 메시지 — feat: 검색 기능 추가'
        self.assertEqual(text.encode('utf-8').decode('utf-8'), text)


if __name__ == '__main__':
    unittest.main()
