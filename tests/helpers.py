"""테스트 공용 도우미. (✅ 구현됨)

모든 연습 테스트는 PracticeTestCase 를 물려받는다. 이 클래스는
    - 테스트 중 실제 네트워크(AI API) 호출을 막고,
    - 진짜 AI_API_KEY 가 테스트에 섞이지 않도록 환경변수에서 잠시 지운다.
"""

import contextlib
import io
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from learning_kit.paths import PRACTICE_DATA_DIR, PROJECT_ROOT
from learning_kit.practice_repo import create_practice_repo

FAKE_KEY = 'test-key-not-real'


class TodoNotDone(NotImplementedError):
    """코드가 아닌 문서(예: README) 단계가 아직 TODO 일 때 쓰는 표시."""


def _network_blocked(*_args, **_kwargs):
    raise RuntimeError(
        '테스트 중에는 실제 네트워크(AI API) 호출이 금지되어 있습니다. '
        'transport 를 끝까지 넘겼는지 확인하세요.'
    )


class PracticeTestCase(unittest.TestCase):
    """연습 테스트의 공통 부모 클래스."""

    def setUp(self):
        super().setUp()
        for target in ('urllib.request.urlopen', 'socket.create_connection'):
            patcher = mock.patch(target, side_effect=_network_blocked)
            patcher.start()
            self.addCleanup(patcher.stop)
        env_patcher = mock.patch.dict(os.environ, {}, clear=False)
        env_patcher.start()
        self.addCleanup(env_patcher.stop)
        os.environ.pop('AI_API_KEY', None)

    # --- 데이터 / 폴더 -----------------------------------------------------
    @staticmethod
    def read_data(name):
        return (PRACTICE_DATA_DIR / name).read_text(encoding='utf-8')

    def make_temp_dir(self):
        temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(temp.cleanup)
        return Path(temp.name)

    def make_repo(self, scenario='feature'):
        """임시 폴더에 연습용 Git 저장소를 만들고 경로 문자열을 돌려준다."""
        return str(create_practice_repo(self.make_temp_dir() / 'repo',
                                        scenario))

    @contextlib.contextmanager
    def inside(self, path):
        """잠시 현재 폴더를 path 로 바꾼다."""
        before = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(before)

    # --- 출력 캡처 ---------------------------------------------------------
    @staticmethod
    def capture(func, *args, **kwargs):
        """func 실행 결과와 화면 출력(stdout+stderr)을 함께 돌려준다.

        argparse 가 SystemExit 을 던지면 그 종료 코드를 결과로 돌려준다.
        """
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), \
                contextlib.redirect_stderr(buffer):
            try:
                result = func(*args, **kwargs)
            except SystemExit as error:
                result = error.code
        return result, buffer.getvalue()


def line_after(output, header_word):
    """header_word 가 들어간 줄 "다음"의 첫 번째 글자 있는 줄을 돌려준다."""
    lines = output.splitlines()
    for index, line in enumerate(lines):
        if header_word in line:
            for next_line in lines[index + 1:]:
                if next_line.strip():
                    return next_line.strip()
    return None


def has_separator(output):
    """'-' 또는 '=' 3개 이상으로만 된 줄이 있는지 확인한다."""
    return any(re.fullmatch(r'\s*[-=]{3,}\s*', line)
               for line in output.splitlines())


__all__ = ['FAKE_KEY', 'PROJECT_ROOT', 'PracticeTestCase', 'TodoNotDone',
           'has_separator', 'line_after']
