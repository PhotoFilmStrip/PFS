#
# Makefile for PhotoFilmStrip
#

appname = photofilmstrip
displayname = PhotoFilmStrip
mkdir = mkdir -p --
srcdir = .


compile:
	python -c "import compileall, re;compileall.compile_dir('.', rx=re.compile('/[.]svn'), force=True, quiet=True)"
	python -OO -c "import compileall, re;compileall.compile_dir('.', rx=re.compile('/[.]svn'), force=True, quiet=True)"
	python setup.py build

clean:
	if [ -e ./dist ] ; then rm -r ./dist ; fi
	find . -name "*.pyc" -exec rm {} ';'
	find . -name "*.pyo" -exec rm {} ';'
	python setup.py clean
	
	rm -f "$(displayname).pot"

pot:
	pygettext -o "$(displayname).pot" -v "$(srcdir)/photofilmstrip"


versioninfo:
	python -c "import photofilmstrip.lib.Settings;print photofilmstrip.lib.Settings.Settings.APP_VERSION"; \


package:
	curdir=`pwd`; \
	ver=`python -c "import photofilmstrip.lib.Settings;print photofilmstrip.lib.Settings.Settings.APP_VERSION"`; \
	appver=`echo $(appname)-$$ver`; \
	releasedir=`echo release_\`date +"%Y_%m_%d"\``; \
	targetdir=`echo $$releasedir/$$appver`; \
	rm -rf $$releasedir; \
	$(mkdir) "$$releasedir"; \
	python setup.py sdist; \
	mv dist/*.tar.gz "$$releasedir/"; \
	cd "$$releasedir"; \
	tar -xzf "$$appver.tar.gz"; \
	cd "$$appver"; \
	dch -d Makefile packaging; \
	debuild --no-tgz-check; \
