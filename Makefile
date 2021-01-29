#!/usr/bin/make -f
# -*- mode:makefile -*-

.PHONY: test
test:
	nosetests3 test

pypi-release:
	$(RM) -r dist
	python3 setup.py sdist
	twine upload dist/*

clean:
	$(RM) -r build prego.egg-info venv dist
	find -name "*flymake*" | xargs $(RM)
