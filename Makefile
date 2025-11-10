#
# Makefile for PhotoFilmStrip
#

displayname = PhotoFilmStrip
srcdir = .
pkgdir = photofilmstrip

all: clean test compile

test:
	pylint --rcfile=.pylintrc --disable=W,R,C $(pkgdir)

compile:
	python3 setup.py build sdist

clean:
	if [ -e ./dist ] ; then rm -r ./dist ; fi
	find . -name "*.pyc" -exec rm {} ';'
	find . -name "*.pyo" -exec rm {} ';'
	find . -name "_scmInfo.py*" -exec rm {} ';'
	find . -name "_pkgInfo.py*" -exec rm {} ';'
	python3 setup.py clean

update-po:
	pygettext3 -o "po/$(displayname).pot" -v "$(srcdir)/$(pkgdir)"
	find po/ -name "*.po" -exec msgmerge --backup=none --update {} "po/$(displayname).pot" ';'


versioninfo:
	python3 -c "from photofilmstrip import Constants;print(Constants.APP_VERSION)"; \
