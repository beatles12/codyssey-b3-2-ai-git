"""기본 환경 테스트 6 — 학습 문서가 준비되어 있고 오프라인으로 볼 수 있다."""

import re
import unittest

from tests.helpers import PROJECT_ROOT

GUIDE = PROJECT_ROOT / 'docs' / 'B3-2_STUDY_GUIDE.html'

REQUIRED_SECTION_IDS = [
    'structure', 'diff-vs-log', 'to-ai', 'api-env', 'commit-flow',
    'pr-flow', 'call-flow', 'function-kinds', 'steps', 'step1', 'step2',
    'step3', 'step4', 'step5', 'step6', 'step7', 'step8', 'test-cases',
    'security-cost', 'auto-test', 'pitch', 'checklist',
]


class StudyGuideTest(unittest.TestCase):

    def setUp(self):
        self.html = GUIDE.read_text(encoding='utf-8')

    def test_has_required_sections(self):
        """교재에 요청된 모든 절(section)이 있다"""
        missing = [section for section in REQUIRED_SECTION_IDS
                   if f'id="{section}"' not in self.html]
        self.assertEqual(missing, [], f'없는 절: {missing}')

    def test_works_offline(self):
        """교재가 인터넷 없이 열린다 (외부 스크립트·스타일·이미지·글꼴 없음)"""
        external = re.findall(
            r'''<(?:script|link|img|iframe|source|video|audio)\b[^>]*'''
            r'''(?:src|href)\s*=\s*["']?(?:https?:)?//''', self.html,
            flags=re.IGNORECASE)
        self.assertEqual(external, [])
        self.assertNotRegex(self.html, r'@import\s+url\(\s*["\']?https?:')
        self.assertNotRegex(self.html, r'url\(\s*["\']?https?:')

    def test_marks_implemented_and_todo(self):
        """교재가 구현됨/TODO/예시 코드를 구분해 표시한다"""
        for marker in ('badge-done', 'badge-todo', 'badge-example'):
            self.assertIn(marker, self.html)


class MarkdownDocsTest(unittest.TestCase):

    def test_practice_steps_has_eight_steps(self):
        """PRACTICE_STEPS.md 에 Step 1~8 이 모두 있다"""
        text = (PROJECT_ROOT / 'docs' / 'PRACTICE_STEPS.md').read_text(
            encoding='utf-8')
        for number in range(1, 9):
            self.assertIn(f'## Step {number}', text)

    def test_start_here_points_to_guides(self):
        """START_HERE.md 가 교재와 실습 명령을 안내한다"""
        text = (PROJECT_ROOT / 'START_HERE.md').read_text(encoding='utf-8')
        for word in ('B3-2_STUDY_GUIDE.html', 'PRACTICE_STEPS.md',
                     'learning_kit.check_env', 'learning_kit.practice'):
            self.assertIn(word, text)


if __name__ == '__main__':
    unittest.main()
