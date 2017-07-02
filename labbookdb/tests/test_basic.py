from labbookdb.db import add

def test_load():
	session, engine = add.loadSession("~/somepath.db")
	session.close()
	engine.dispose()
