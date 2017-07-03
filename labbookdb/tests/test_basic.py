from labbookdb.db import add

def test_load():
	session, engine = add.load_session("~/somepath.db")
	session.close()
	engine.dispose()
