__author__ = "Horea Christian"

import argh

try:
	from report.tracking import further_cages, animal_id_table
	from db.query import animal_info
except ImportError:
	from .report.tracking import further_cages, animal_id_table
	from .db.query import animal_info

def main():
	argh.dispatch_commands([animal_info, further_cages, animal_id_table])

if __name__ == '__main__':
	main()
