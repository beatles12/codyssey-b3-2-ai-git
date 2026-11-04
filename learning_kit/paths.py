"""프로젝트 안의 주요 폴더 위치. (✅ 구현됨)"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRACTICE_DATA_DIR = PROJECT_ROOT / 'practice_data'
PRACTICE_REPO_DIR = PROJECT_ROOT / 'practice_repo'
GUIDE_PATH = PROJECT_ROOT / 'docs' / 'B3-2_STUDY_GUIDE.html'
STEPS_PATH = PROJECT_ROOT / 'docs' / 'PRACTICE_STEPS.md'


def read_practice_file(name):
    """practice_data 폴더의 파일 내용을 UTF-8 문자열로 읽는다."""
    return (PRACTICE_DATA_DIR / name).read_text(encoding='utf-8')
