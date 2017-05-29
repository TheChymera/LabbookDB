from setuptools import setup

if __name__ == '__main__':
	setup(
		name="LabbookDB",
		version="0.0.1",
		description = "A Wet-Work-Tracking Database Application Framework",
		author = "Horea Christian",
		author_email = "horea.christ@yandex.com",
		url = "https://github.com/TheChymera/LabbookDB",
		keywords = [
			"laboratory notebook",
			"labbook",
			"wet work",
			"record keeping",
			"reports",
			"life science",
			"biology",
			"neuroscience",
			"behaviour",
			"relational database",
			"SQL",
			],
		classifiers = [],
		install_requires = [],
		provides = ["labbookdb"],
		packages = [
			"labbookdb",
			"labbookdb.db",
			"labbookdb.evaluate",
			"labbookdb.introspection",
			"labbookdb.report",
			],
		entry_points = {'console_scripts' : \
				['LDB = labbookdb.cli:main']
			}
		)
