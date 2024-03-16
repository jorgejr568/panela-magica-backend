test:
	pytest .

test-verbose:
	pytest -v .

test-coverage:
	pytest --cov .
	@rm .coverage