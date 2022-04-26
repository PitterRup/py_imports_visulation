import pytest

from src.app import get_imports, import_to_abs_import

@pytest.mark.parametrize('code, expected', [
    ('', []),
    ('import sys', ['sys']),
    ('#import sys', []),
    ('import sys  as   sysalias', ['sys']),
    ('import sys.test', ['sys.test']),
    ('import sys.test, re.test2', ['sys.test', 're.test2']),
    ('from re import match', ['re.match']),    
    ('from re.test import match', ['re.test.match']),
    ('from re import match, search', ['re.match', 're.search']),
    ('from re.test import match, search', ['re.test.match', 're.test.search']),
    (
        '''
from sys import (
    test1,
    test2,
    test3 as testalias,
)
import re''',
        ['sys.test1', 'sys.test2', 'sys.test3', 're']
    ),
    (
        '''# test many imports
print('test many import')
import sys
print('test many imports')
#import sys2
from re import match''',
        ['sys', 're.match']
    ),    
])
def test_get_imports(code, expected):
    assert get_imports(code.splitlines()) == expected


@pytest.mark.parametrize('filetuple, imp, expected', [
    (('app', 'db_util'), '.test.bb1', 'app.db_util.test.bb1'),
    (('app', 'db_util'), '..test.bb1', 'app.test.bb1'),
    (('app', 'db_util'), '...test.bb1', 'test.bb1'),
    (('app', 'db_util'), 'app.test.bb1', 'app.test.bb1'),
])
def test_import_to_abs_import(filetuple, imp, expected):
    assert import_to_abs_import(imp, filetuple) == expected

def test_import_to_abs_import_raises():
    with pytest.raises(ValueError):
        import_to_abs_import('....test.bb1', ('app', 'db_util'))