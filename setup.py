from setuptools import setup

if __name__ == '__main__':
	setup(
		name="LabbookDB",
		version="",
		description = "Database lab book standard with information addition, retrieval, and reporting functions",
		author = "Horea Christian",
		author_email = "horea.christ@yandex.com",
		url = "https://github.com/TheChymera/LabbookDB",
		keywords = ["lab book", "science", "database", "analysis", "reports", "statistics"],
		classifiers = [],
		install_requires = [],
		provides = ["labbookdb"],
		packages = ["labbookdb",
			"labbookdb.db",
			"labbookdb.report",
			],
		entry_points = {'console_scripts' : \
				['LDB = labbookdb.cli:main']
			}
		)
