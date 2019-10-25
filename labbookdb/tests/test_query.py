import pytest

from labbookdb.db import add

def test_related_entry_separators():
	session, engine = add.load_session("/tmp/somepath.db")
	with pytest.raises(BaseException) as excinfo:
		add.get_related_ids(session, engine, "Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC/cdb&#&identifier.275511")
	assert excinfo.value.args[0] == 'No entry was found with a value of "275511" on the "identifier" column of the "AnimalExternalIdentifier" CATEGORY, in the database.'
	with pytest.raises(BaseException) as excinfo:
		add.get_related_ids(session, engine, "Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC/cdb&&identifier.275511")
	assert excinfo.value.args[0] == 'No entry was found with a value of "ETH/AIC/cdb" on the "database" column of the "AnimalExternalIdentifier" CATEGORY, in the database.'
