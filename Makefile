#!/usr/bin/make -f
# -*- mode:makefile -*-

.PHONY: test
test:
	nosetests3 test

release:
	python3 setup.py sdist upload

clean:
	$(RM) -r build prego.egg-info venv dist
	find -name "*flymake*" | xargs $(RM)
