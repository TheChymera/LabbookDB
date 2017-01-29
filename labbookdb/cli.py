__author__ = "Horea Christian"

import argh

#the order here is very important, if these modules are called in the wrong order, the declarative based will end up being regenerated and will complain about duplicates along the lines of:
#sqlalchemy.exc.InvalidRequestError: Table 'genotype_associations' is already defined for this MetaData instance.  Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
try:
	from db.query import animal_info
	from report.tracking import further_cages, animal_id_table
except ImportError:
	from .db.query import animal_info
	from .report.tracking import further_cages, animal_id_table

def main():
	argh.dispatch_commands([animal_info, further_cages, animal_id_table])

if __name__ == '__main__':
	main()
