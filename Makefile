.PHONY: all
all: virtualenv requirements

.PHONY: virtualenv
virtualenv: bin/

bin/:
	virtualenv .

.PHONY:requirements
requirements:
	bin/pip install -r requirements.txt
