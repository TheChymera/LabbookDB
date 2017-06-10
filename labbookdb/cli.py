__author__ = "Horea Christian"

import argh

#the order here is very important, if these modules are called in the wrong order, the declarative base will end up being regenerated and will complain about duplicates along the lines of:
#sqlalchemy.exc.InvalidRequestError: Table 'genotype_associations' is already defined for this MetaData instance.  Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
#OR
#ImportError: Gtk3 backend requires pygobject to be installed.
from labbookdb.report.tracking import further_cages, animals_id, animals_info
from .db.add import add_generic, append_parameter
from .db.query import animal_info, cage_info

def main():
	argh.dispatch_commands([
		add_generic,
		animal_info,
		animals_id,
		animals_info,
		append_parameter,
		cage_info,
		further_cages,
		])

if __name__ == '__main__':
	main()
