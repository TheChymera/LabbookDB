from labbookdb.db import add

def test_load():
	session, engine = add.load_session("/tmp/somepath.db")
	session.close()
	engine.dispose()
