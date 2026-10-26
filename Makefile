PYTHON ?= python3

.PHONY: help install uninstall generate example validate check clean

help:
	@echo "caelestia-opencode-theme"
	@echo ""
	@echo "  make install     symlink the generator, wire Caelestia + OpenCode, generate the theme"
	@echo "  make uninstall   undo the above"
	@echo "  make generate    regenerate the installed theme now"
	@echo "  make example     refresh examples/caelestia.json from the current scheme"
	@echo "  make validate    validate examples/caelestia.json"
	@echo "  make check       regenerate to a temp file and validate it"
	@echo "  make clean       remove caches"

install:
	$(PYTHON) install.py

uninstall:
	$(PYTHON) uninstall.py

generate:
	./caelestia-opencode-theme

example:
	./caelestia-opencode-theme --stdout --no-nudge > examples/caelestia.json
	@echo "wrote examples/caelestia.json"

validate:
	$(PYTHON) validate.py examples/caelestia.json

check:
	./caelestia-opencode-theme --stdout --no-nudge > /tmp/caelestia-theme.json
	$(PYTHON) validate.py /tmp/caelestia-theme.json

clean:
	rm -rf __pycache__ */__pycache__ .venv venv
