import unittest
from pathlib import Path
from src.Structure import create_file, create_structure

class TestFileCreation(unittest.TestCase):
    """Pruebas unitarias para la creación de archivos y directorios."""

    def test_create_file(self):
        temp_dir = Path('./test_dir')
        temp_dir.mkdir(parents=True, exist_ok=True)
        test_file = temp_dir / 'test_file.txt'
        message = create_file(test_file, "Test content")
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "Test content")
        test_file.unlink()
        temp_dir.rmdir()

    def test_create_directory(self):
        temp_dir = Path('./test_dir')
        create_structure(temp_dir, [{'path': 'sub_dir', 'type': 'directory'}])
        self.assertTrue((temp_dir / 'sub_dir').exists())
        temp_dir.rmdir()

if __name__ == "__main__":
    unittest.main()
