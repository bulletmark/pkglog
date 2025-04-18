NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))
PYFILES = $(PYNAME)/*.py $(PYNAME)/*/*.py

check:
	ruff check $(PYFILES)
	mypy $(PYFILES)
	vermin -vv --exclude importlib.metadata --exclude tomllib \
		--no-tips -i $(PYFILES)

upload: build
	uv-publish

build:
	rm -rf dist
	uv build

doc:
	update-readme-usage

format:
	ruff check --select I --fix $(PYFILES) && ruff format $(PYFILES)

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
