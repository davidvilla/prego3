#!/usr/bin/make -f
# -*- mode:makefile -*-

.PHONY: test
test:
	nosetests3 test

pypi-release:
	$(RM) -r dist
	python3 setup.py sdist
	twine upload --repository prego3 dist/*

clean:
	$(RM) -r build prego.egg-info venv dist .tox
	find -name "*flymake*" | xargs $(RM)
