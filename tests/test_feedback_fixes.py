import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import storage
from quiz import Quiz
from quiz_game import QuizGame


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'state.json'
        self.patch = patch.object(storage, 'STATE_PATH', self.path)
        self.patch.start()
        storage._blocked_paths.clear()
        storage._archived_versions.clear()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.data = storage.create_default_state()

    def tearDown(self):
        self.output.__exit__(None, None, None)
        self.patch.stop()
        self.temp.cleanup()

    def test_first_save_and_reload(self):
        self.assertTrue(storage.save_state(self.data))
        self.assertEqual(storage.load_state(), self.data)
        self.assertEqual(len(storage.list_backups()), 1)

    def test_unchanged_save_creates_no_extra_backup(self):
        storage.save_state(self.data)
        storage.save_state(self.data)
        self.assertEqual(len(storage.list_backups()), 1)

    def test_previous_version_is_backed_up(self):
        storage.save_state(self.data)
        changed = copy.deepcopy(self.data)
        changed['best_score'] = 50
        storage.save_state(changed)
        self.assertEqual(storage._read_state(storage.list_backups()[0]), self.data)
        self.assertEqual(storage.load_state(), changed)

    def test_corrupt_file_recovers_without_losing_raw_bytes(self):
        storage.save_state(self.data)
        broken = b'{broken json'
        self.path.write_bytes(broken)
        self.assertEqual(storage.load_state(), self.data)
        preserved = list(storage.backup_directory().glob('corrupt-*.json'))
        self.assertEqual(preserved[0].read_bytes(), broken)
        self.assertTrue(storage.save_state(self.data))
        self.assertEqual(storage.load_state(), self.data)

    def test_missing_file_recovers_backup(self):
        storage.save_state(self.data)
        self.path.unlink()
        self.assertEqual(storage.load_state(), self.data)

    def test_invalid_latest_backup_is_skipped(self):
        storage.save_state(self.data)
        (storage.backup_directory() / 'state-99999999.json').write_text('bad')
        self.path.write_text('bad')
        self.assertEqual(storage.load_state(), self.data)

    def test_no_backups_uses_defaults_and_preserves_corrupt(self):
        self.path.write_text('bad')
        self.assertEqual(storage.load_state(), self.data)
        self.assertTrue(list(storage.backup_directory().glob('corrupt-*.json')))

    def test_read_permission_error_blocks_exit_save(self):
        storage.save_state(self.data)
        before = self.path.read_bytes()
        with patch('pathlib.Path.open', side_effect=PermissionError('test')):
            storage.load_state()
        changed = copy.deepcopy(self.data)
        changed['best_score'] = 5
        self.assertFalse(storage.save_state(changed))
        self.assertEqual(self.path.read_bytes(), before)

    def test_backup_failure_does_not_overwrite_state(self):
        storage.save_state(self.data)
        before = self.path.read_bytes()
        changed = copy.deepcopy(self.data)
        changed['best_score'] = 25
        with patch.object(storage, 'create_backup', side_effect=OSError('disk full')):
            self.assertFalse(storage.save_state(changed))
        self.assertEqual(self.path.read_bytes(), before)

    def test_replace_failure_keeps_original(self):
        storage.save_state(self.data)
        before = self.path.read_bytes()
        changed = copy.deepcopy(self.data)
        changed['best_score'] = 25
        with patch('pathlib.Path.replace', side_effect=OSError('replace failure')):
            self.assertFalse(storage.save_state(changed))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse(self.path.with_suffix('.json.tmp').exists())

    def test_keep_five_snapshots(self):
        for score in range(9):
            self.data['best_score'] = score
            self.assertTrue(storage.save_state(self.data))
        self.assertEqual(len(storage.list_backups()), 5)

    def test_manual_restore_preserves_current(self):
        storage.save_state(self.data)
        old = storage.list_backups()[0]
        self.data['best_score'] = 60
        storage.save_state(self.data)
        self.assertTrue(storage.restore_backup(old))
        self.assertIsNone(storage.load_state()['best_score'])
        saved = list(storage.backup_directory().glob('before-restore-*.json'))
        self.assertEqual(storage._read_state(saved[0])['best_score'], 60)

    def test_restore_rejects_external_path_and_corrupt_backup(self):
        external = Path(self.temp.name) / 'state-external.json'
        external.write_text(json.dumps(self.data))
        self.assertFalse(storage.restore_backup(external))
        target = storage._unique_path('state')
        target.write_text('bad')
        self.assertFalse(storage.restore_backup(target))
        self.assertFalse(self.path.exists())

    def test_utf8_bom_is_supported(self):
        self.path.write_text(json.dumps(self.data), encoding='utf-8-sig')
        self.assertEqual(storage.load_state(), self.data)

    def test_invalid_history_and_boolean_answer_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['history'] = [42]
        with self.assertRaises(ValueError):
            storage.validate_state(bad)
        bad = copy.deepcopy(self.data)
        bad['quizzes'][0]['answer'] = True
        with self.assertRaises(ValueError):
            storage.validate_state(bad)

    def test_empty_quizzes_stay_empty(self):
        self.data['quizzes'] = []
        storage.save_state(self.data)
        self.assertEqual(storage.load_state()['quizzes'], [])

    def test_cli_list_and_missing_restore(self):
        storage.save_state(self.data)
        with patch('sys.argv', ['backup_state.py', 'list']):
            import backup_state
            self.assertEqual(backup_state.main(), 0)
        with patch('sys.argv', ['backup_state.py', 'restore', 'latest']):
            self.assertEqual(backup_state.main(), 0)


class PaginationTests(unittest.TestCase):
    def setUp(self):
        self.game = QuizGame.__new__(QuizGame)
        self.game.quizzes = [Quiz(str(i), ['a', 'b', 'c', 'd'], 1) for i in range(1000)]

    def test_first_page_does_not_print_all_thousand(self):
        out = io.StringIO()
        with patch('builtins.input', return_value='0'), contextlib.redirect_stdout(out):
            self.game.list_quizzes()
        result = out.getvalue()
        self.assertIn('20. 19', result)
        self.assertNotIn('21. 20', result)
        self.assertIn('1/50', result)

    def test_forward_backward_navigation(self):
        with patch('builtins.input', side_effect=['1', '2', '0']), contextlib.redirect_stdout(io.StringIO()):
            numbers = [n for n, _ in self.game.iter_pages(self.game.quizzes, 'test')]
        self.assertEqual(numbers, list(range(1,21)) + list(range(21,41)) + list(range(1,21)))

    def test_history_newest_first(self):
        with patch('builtins.input', return_value='0'), contextlib.redirect_stdout(io.StringIO()):
            rows = list(self.game.iter_pages(list(range(1000)), 'test', reverse=True))
        self.assertEqual(rows[0], (1, 999))
        self.assertEqual(rows[-1], (20, 980))

    def test_delete_uses_global_index_after_pagination(self):
        self.game.save_data = lambda: True
        with patch('builtins.input', side_effect=['1', '0', '25', '1']), contextlib.redirect_stdout(io.StringIO()):
            self.game.delete_quiz()
        self.assertEqual(len(self.game.quizzes), 999)
        self.assertEqual(self.game.quizzes[24].question, '25')


if __name__ == '__main__':
    unittest.main()
