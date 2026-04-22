#!/usr/bin/make -f

.PHONY: test
test:
	pytest test

pypi-release:
	$(RM) -r dist
	python3 setup.py sdist
	twine upload --repository prego3 dist/*

clean:
	$(RM) -r build prego.egg-info venv dist .tox
	find -name "*flymake*" | xargs $(RM)
