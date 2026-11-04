"""Step 2 연습 테스트 — Git 변경 사항 수집 (ai_gitgen/git_collector.py)

실행: python -m learning_kit.practice 2
테스트마다 임시 폴더에 연습용 Git 저장소를 새로 만들어 사용한다.
"""

import unittest

from ai_gitgen import git_collector as gc
from tests.helpers import PracticeTestCase

EXPECTED_SAMPLE = [
    {'code': 'M', 'path': 'README.md'},
    {'code': 'M', 'path': 'todo_app/app.py'},
    {'code': 'A', 'path': 'todo_app/search.py'},
    {'code': 'MM', 'path': 'todo_app/settings.py'},
    {'code': 'D', 'path': 'old_script.py'},
    {'code': 'R', 'path': 'docs/guide.md'},
    {'code': '??', 'path': 'NOTES.md'},
]


class RunGitTest(PracticeTestCase):

    def test_returns_stdout_string(self):
        """run_git(['--version']) 은 'git version ...' 문자열을 돌려준다"""
        output = gc.run_git(['--version'])
        self.assertIsInstance(output, str)
        self.assertTrue(output.startswith('git version'))

    def test_failure_raises_git_command_error(self):
        """실패한 git 명령은 GitCommandError 를 발생시킨다"""
        with self.assertRaises(gc.GitCommandError):
            gc.run_git(['this-is-not-a-git-command'])

    def test_runs_in_given_folder(self):
        """cwd 로 준 폴더에서 실행된다"""
        repo = self.make_repo('feature')
        output = gc.run_git(['branch', '--show-current'], cwd=repo)
        self.assertEqual(output.strip(), 'feature/add-search')


class IsGitRepositoryTest(PracticeTestCase):

    def test_true_inside_repository(self):
        """연습 저장소 안이면 True"""
        self.assertIs(gc.is_git_repository(self.make_repo('clean')), True)

    def test_false_outside_repository(self):
        """Git 저장소가 아닌 빈 폴더면 (예외 없이) False"""
        self.assertIs(gc.is_git_repository(str(self.make_temp_dir())), False)


class ParseStatusTest(PracticeTestCase):

    def test_parse_sample(self):
        """practice_data/git_status_sample.txt 7가지 상태를 모두 읽는다"""
        result = gc.parse_status_output(
            self.read_data('git_status_sample.txt'))
        self.assertEqual(result, EXPECTED_SAMPLE)

    def test_leading_space_is_kept(self):
        """' M app.py' 처럼 앞이 공백인 줄도 경로가 잘리지 않는다"""
        self.assertEqual(gc.parse_status_output(' M app.py\n'),
                         [{'code': 'M', 'path': 'app.py'}])

    def test_rename_uses_new_name(self):
        """이름 바꾸기 'R  old -> new' 는 새 이름만 path 로 쓴다"""
        self.assertEqual(gc.parse_status_output('R  a.txt -> b.txt'),
                         [{'code': 'R', 'path': 'b.txt'}])

    def test_empty_text(self):
        """빈 문자열이나 빈 줄만 있으면 []"""
        self.assertEqual(gc.parse_status_output(''), [])
        self.assertEqual(gc.parse_status_output('\n\n'), [])


class ChangedFilesTest(PracticeTestCase):

    def test_feature_repo_files(self):
        """feature 저장소: README.md, todo_app/app.py, todo_app/search.py"""
        files = gc.get_changed_files(self.make_repo('feature'))
        paths = sorted(item['path'] for item in files)
        self.assertEqual(paths, ['README.md', 'todo_app/app.py',
                                 'todo_app/search.py'])

    def test_clean_repo_has_no_files(self):
        """변경이 없는 저장소는 []"""
        self.assertEqual(gc.get_changed_files(self.make_repo('clean')), [])

    def test_untracked_file_is_listed(self):
        """새 파일(추적 안 됨, ??)도 목록에 나온다"""
        files = gc.get_changed_files(self.make_repo('untracked-only'))
        self.assertEqual(files, [{'code': '??', 'path': 'NOTES.md'}])


class DiffTest(PracticeTestCase):

    def test_unstaged_change_is_included(self):
        """git add 안 한 변경(unstaged)이 diff 에 들어 있다"""
        diff = gc.get_diff(self.make_repo('unstaged-only'))
        self.assertIn('complete_todo', diff)

    def test_staged_change_is_included(self):
        """git add 한 변경(staged)도 diff 에 들어 있다 (--cached)"""
        diff = gc.get_diff(self.make_repo('staged-only'))
        self.assertIn('search_todos', diff)

    def test_both_staged_and_unstaged(self):
        """feature 저장소: staged 와 unstaged 변경이 모두 들어 있다"""
        diff = gc.get_diff(self.make_repo('feature'))
        self.assertIn('search_todos', diff)
        self.assertIn('complete_todo', diff)
        self.assertEqual(diff.count('diff --git '), 3)

    def test_clean_repo_diff_is_empty(self):
        """변경이 없으면 diff 는 빈 문자열(공백뿐)이다"""
        self.assertEqual(gc.get_diff(self.make_repo('clean')).strip(), '')

    def test_count_diff_lines(self):
        """count_diff_lines: 3줄이면 3, 빈 문자열이면 0"""
        self.assertEqual(gc.count_diff_lines('a\nb\nc\n'), 3)
        self.assertEqual(gc.count_diff_lines('a\nb\nc'), 3)
        self.assertEqual(gc.count_diff_lines(''), 0)
        sample = self.read_data('git_diff_sample.diff')
        self.assertEqual(gc.count_diff_lines(sample), 46)


class BranchTest(PracticeTestCase):

    def test_current_branch(self):
        """현재 브랜치 이름을 앞뒤 공백 없이 돌려준다"""
        self.assertEqual(gc.get_current_branch(self.make_repo('feature')),
                         'feature/add-search')
        self.assertEqual(gc.get_current_branch(self.make_repo('bugfix')),
                         'fix/empty-title')


if __name__ == '__main__':
    unittest.main()
