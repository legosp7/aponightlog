import sqlite3
import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()  # Ensure the same DB instance is returned
        
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')  # Should raise an error since DB is closed
        
    assert 'closed' in str(e.value)
        

        
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True
        
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized the database.' in result.output
    assert Recorder.called