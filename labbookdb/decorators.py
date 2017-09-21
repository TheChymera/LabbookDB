import os
from argh import arg

def environment_db_path():
        """Add a default value to the `db_path` positional argument, based on the `LDB_PATH` environment variable, and fail elegantly if not."""
        try:
                return arg("db_path",
                        default=os.environ["LDB_PATH"],
                        nargs="?",
                        help="The path of the LabbookDB database file to query. "
                                "We detect that your `LDB_PATH` environment variable is set to `{}` in this prompt. "
                                "This is automatically used by LabbookDB if no custom value is specified.".format(os.environ["LDB_PATH"]),
                        )
        except KeyError:
                return arg("db_path",
                        help="The path of the LabbookDB database file to query. "
                                "We detect that your `LDB_PATH` environment variable IS NOT set in this prompt. "
                                "This environment variable can be automatically used by LabbookDB if no custom value is specified.",
                        )

