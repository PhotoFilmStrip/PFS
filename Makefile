#
# Makefile for PhotoFilmStrip
#
include Makefile.rules


compile:
	python -c "import compileall, re;compileall.compile_dir('.', rx=re.compile('/[.]svn'), force=True, quiet=True)"
	python -OO -c "import compileall, re;compileall.compile_dir('.', rx=re.compile('/[.]svn'), force=True, quiet=True)"
	
	target=`echo $@`; \
	make -C po $$target

clean:
	if [ -e ./dist ] ; then rm -r ./dist ; fi
	find . -name "*.pyc" -exec rm {} ';'
	find . -name "*.pyo" -exec rm {} ';'
	
	target=`echo $@`; \
	make -C po $$target

	rm -f "$(displayname).pot"

install:
	$(mkdir) "$(DESTDIR)$(appdir)"
	cp -r "$(srcdir)/src/cli/" "$(DESTDIR)$(appdir)"
	cp -r "$(srcdir)/src/core/" "$(DESTDIR)$(appdir)"
	cp -r "$(srcdir)/src/gui/" "$(DESTDIR)$(appdir)"
	cp -r "$(srcdir)/src/lib/" "$(DESTDIR)$(appdir)"
	cp -r "$(srcdir)/src/res/" "$(DESTDIR)$(appdir)" 
	cp "$(srcdir)/src/$(appname)-cli.py" "$(DESTDIR)$(appdir)/"
	cp "$(srcdir)/src/$(appname)-gui.py" "$(DESTDIR)$(appdir)/"
	
	$(mkdir) "$(DESTDIR)$(desktopdir)"
	cp "$(srcdir)/build/$(appname).desktop" "$(DESTDIR)$(desktopdir)/"
	$(mkdir) "$(DESTDIR)$(pixmapdir)"
	cp "$(srcdir)/build/$(appname).xpm" "$(DESTDIR)$(pixmapdir)/"
	
	$(mkdir) "$(DESTDIR)$(bindir)"
	cp "$(srcdir)/build/$(appname)" "$(DESTDIR)$(bindir)/"
	
	target=`echo $@`; \
	make -C po $$target

uninstall:
	rm -Rf "$(DESTDIR)$(appdir)"
	rm -f "$(DESTDIR)$(desktopdir)/$(appname).desktop"
	rm -f "$(DESTDIR)$(pixmapdir)/$(appname).xpm"
	rm -f "$(DESTDIR)$(bindir)/$(appname)"
	
	target=`echo $@`; \
	make -C po $$target

pot:
	pygettext -o "$(displayname).pot" -v "$(srcdir)/src"

