__author__ = "Horea Christian"

import argh
from report.tracking import animal_info, further_cages, animal_id_table

def main():
	argh.dispatch_commands([animal_info, further_cages, animal_id_table])

if __name__ == '__main__':
	main()
