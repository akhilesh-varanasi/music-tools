.PHONY: desktop-dev desktop-dev-all desktop-build-ui desktop-package desktop-run-dist

desktop-dev:
	python -m desktop.tasks dev

desktop-dev-all:
	python -m desktop.tasks dev --with-vite

desktop-build-ui:
	python -m desktop.tasks build-ui

desktop-package:
	python -m desktop.tasks package

desktop-run-dist:
	python -m desktop.tasks run-dist
