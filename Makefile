test:
	python setup.py test

flake8:
	flake8 --ignore=E501,E225,E128,W391,W404,F403 partialize

install:
	python setup.py install

develop:
	python setup.py develop

coverage:
	coverage run tests.py
