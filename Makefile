.PHONY: all
all: virtualenv requirements

virtualenv: bin/

bin/:
	virtualenv .

.PHONY:requirements
requirements:
	bin/pip install -r requirements.txt
