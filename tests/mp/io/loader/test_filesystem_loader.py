from mp.io.loader.filesystem_loader import FilesystemLoader


def test_filesystemloader():
    expected = '/fake/file/path'
    under_test = FilesystemLoader(expected)
    actual = under_test.file_path()
    assert expected == actual
