__author__ = "Horea Christian"

import argh
from report.tracking import further_cages, animals_id, animals_info
from db.query import animal_info

def main():
	argh.dispatch_commands([animal_info, further_cages, animals_id, animals_info])

if __name__ == '__main__':
	main()
