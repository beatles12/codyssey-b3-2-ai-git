"""Step 8 연습 테스트 — 제출용 README.md (공식 요구사항 6. 리포지토리 및 문서화)

실행: python -m learning_kit.practice 8

README.md 에 'TODO(Step 8)' 표시가 남아 있으면 [TODO] 로 보인다.
README 작성 틀: docs/templates/README_TEMPLATE.md
"""

import re
import unittest

from tests.helpers import PROJECT_ROOT, PracticeTestCase, TodoNotDone

# (확인 항목, 그중 하나라도 있으면 통과하는 단어들)
README_REQUIREMENTS = [
    ('설치 및 실행 방법', ['설치', 'install']),
    ('환경변수(API Key) 설정 방법', ['AI_API_KEY']),
    ('커밋 생성 명령 사용 예시',
     ['python main.py commit', 'python3 main.py commit']),
    ('PR 생성 명령 사용 예시', ['python main.py pr', 'python3 main.py pr']),
    ('출력 예시 — 커밋 메시지', ['Commit Message']),
    ('출력 예시 — PR 본문 (Why)', ['## Why']),
    ('출력 예시 — PR 본문 (What)', ['## What']),
    ('출력 예시 — PR 본문 (How to Test)', ['## How to Test']),
    ('CLI 옵션 설명', ['--temperature', '--max-tokens']),
    ('민감정보 대응 또는 비용/요청 횟수 안내',
     ['민감', 'safe-mode', '비용', '요청 횟수', '마스킹']),
]


class ReadmeTest(PracticeTestCase):

    def setUp(self):
        super().setUp()
        self.readme = (PROJECT_ROOT / 'README.md').read_text(encoding='utf-8')
        if 'TODO(Step 8)' in self.readme:
            raise TodoNotDone('Step 8 - README.md 를 제출용으로 작성하세요.')
        if '✏️' in self.readme:
            raise TodoNotDone('Step 8 - README.md 에 아직 채우지 않은 ✏️ 칸이 '
                              '남아 있습니다.')

    def test_required_contents(self):
        """README 에 공식 필수 내용이 모두 있다"""
        lower = self.readme.lower()
        missing = [label for label, words in README_REQUIREMENTS
                   if not any(word.lower() in lower for word in words)]
        self.assertEqual(missing, [], f'README 에 없는 내용: {missing}')

    def test_no_real_key_in_readme(self):
        """README 의 키 예시는 가짜 값(YOUR_KEY 등)이다"""
        for match in re.finditer(r'AI_API_KEY\s*=\s*["\']?([^"\'\s]+)',
                                 self.readme):
            value = match.group(1)
            with self.subTest(value=value[:6]):
                self.assertRegex(
                    value, r'(?i)your|fake|example|xxx|<|\$|여기|키',
                    '진짜 키처럼 보이는 값이 있습니다. YOUR_KEY 같은 '
                    '자리표시로 바꾸세요.')

    def test_explains_review_before_use(self):
        """AI 결과는 검토 후 사용한다는 안내가 있다 (공식 제약)"""
        self.assertTrue(any(word in self.readme for word in
                            ('검토', 'review', '확인 후')))


if __name__ == '__main__':
    unittest.main()
