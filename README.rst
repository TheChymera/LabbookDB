LabbookDB
=========

.. image:: https://readthedocs.org/projects/labbookdb/badge/?version=latest
  :target: http://labbookdb.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status
.. image:: https://travis-ci.org/TheChymera/LabbookDB.svg?branch=master
  :target: https://travis-ci.org/TheChymera/LabbookDB

This package contains a relational database structure for life science research, and a number of functions to conveniently add and retrieve information - and generate summaries.
The core concept of LabbookDB is that most of the information classically tracked in a lab book can be more efficiently and more reliably stored in a relational database.

In comparison to a paper notebook, an **electronic** lab book is:

* More easily stored
* More easily shared
* More easily backed up

In comparison with other electronic formats based on a document concept, a **database** of experimental metadata is:

* More easily browsed
* More easily queried
* More easily integrated into data analysis functions

Presentations
-------------

Video
~~~~~

* `LabbookDB - A Relational Framework for Laboratory Metadata <https://www.youtube.com/watch?v=FKWznqP6rcE>`_, at SciPy 2017 in Austin (TX,USA).

Publications
~~~~~~~~~~~~

* `LabbookDB - A Wet-Work-Tracking Database Application Framework <https://www.researchgate.net/publication/319855508_LabbookDB_A_Wet-Work-Tracking_Database_Application_Framework>`_, in Proceedings of the 15th Python in Science Conference (SciPy 2017).

Installation
------------

Gentoo Linux
~~~~~~~~~~~~

LabbookDB is available for Portage (the package manager of Gentoo Linux, derivative distributions, as well as BSD) via the `Chymeric Overlay <https://github.com/TheChymera/overlay>`_.
Upon enabling the overlay, the package can be emerged:

.. code-block:: console

    emerge labbookdb


Python Package Manager (Users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python's `setuptools` allows you to install Python packages independently of your distribution (or operating system, even).
This approach cannot manage any of our numerous non-Python dependencies (by design) and at the moment will not even manage Python dependencies;
as such, given any other alternative, **we do not recommend this approach**:

.. code-block:: console

    git clone git@github.com:TheChymera/LabbookDB.git
    cd LabbookDB
    python setup.py install --user

Python Package Manager (Developers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python's `setuptools` allows you to install Python packages independently of your distribution (or operating system, even);
it also allows you to install a "live" version of the package - dynamically linking back to the source code.
This permits you to test code (with real module functionality) as you develop it.
This method is sub-par for dependency management (see above notice), but - as a developer - you should be able to manually ensure that your package manager provides the needed packages.

.. code-block:: console

    git clone git@github.com:TheChymera/LabbookDB.git
    cd LabbookDB
    mkdir ~/.python_develop
    echo "export PYTHONPATH=\$HOME/.python_develop:\$PYTHONPATH" >> ~/.bashrc
    echo "export PATH=\$HOME/.python_develop:\$PATH" >> ~/.bashrc
    source ~/.bashrc
    python setup.py develop --install-dir ~/.python_develop/

Example Input
-------------

LabbookDB is designed to organize complex wet work data.
We publish example input to generate a relationship-rich database in a separate repository, `demolog <https://bitbucket.org/TheChymera/demolog>`_.

Dependencies
------------

* `Argh`_
* `Pandas`_
* `simplejson`_
* `SQLAlchemy`_

Optional Dependencies for Introspection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `Sadisplay`_

Optional Dependencies for PDF Protocol Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `TeX Live`_

Optional Dependencies for Plotting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* `BehavioPy`_
* `Matplotlib`_


.. _Argh: https://github.com/neithere/argh/
.. _BehavioPy: https://github.com/TheChymera/behaviopy
.. _Matplotlib: https://matplotlib.org/
.. _Pandas: http://pandas.pydata.org/
.. _Sadisplay: https://bitbucket.org/estin/sadisplay/wiki/Home
.. _simplejson: https://github.com/simplejson/simplejson
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _TeX Live: https://www.tug.org/texlive/
