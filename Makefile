.PHONY: default clean coverage _docs docs dtest format lint pages pre-commit test typecheck

PYTEST_CMD = pytest air
TEST_CMD = PYTHONPATH='.' $(PYTEST_CMD)

default:
	echo "Hello, World!"

clean:
	find air -type f -name "*.py[co]" -delete -o -type d -name __pycache__ -delete
	rm -f .coverage
	rm -rf .ipynb_checkpoints
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf dist

coverage:
	coverage run -m $(PYTEST_CMD)
	coverage report -m

lint:
	python -m pre_commit_hooks.debug_statement_hook air/**/*.py
	isort air --recursive --check-only
	black air --check
	flake8 air

# the order is important
pre-commit: clean lint test typecheck

format:
	isort air --recursive -y
	black air

test:
	$(TEST_CMD) $(ARGV)

typecheck:
	mypy air
