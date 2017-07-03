from labbookdb.db import add

def test_related_entry_separators():
	session, engine = add.load_session("~/somepath.db")
	with pytest.raises(Exception) as excinfo:
		add.get_related_ids(s,e,"Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC/cdb&#&identifier.275511")
	assert excinfo.value.args[0] == 'No entry was found with a value of "275511" on the "identifier" column of the "AnimalExternalIdentifier" CATEGORY, in the database.'
	with pytest.raises(Exception) as excinfo:
		add.get_related_ids(s,e,"Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC/cdb&&identifier.275511")
	assert excinfo.value.args[0] == 'No entry was found with a value of "ETH/AIC/cdb" on the "database" column of the "AnimalExternalIdentifier" CATEGORY, in the database.'
