#
# Makefile for PhotoFilmStrip
#
include ../Makefile.rules


compile:
	for poFile in *.po; do \
	    lang=$${poFile%.*}; \
	    msgfmt -o "$$lang.mo" "$$lang.po"; \
	done

clean:
	find . -name "*.mo" -exec rm {} ';'

install:
	$(mkdir) "$(DESTDIR)$(localedir)"
	for moFile in *.mo; do \
	    lang=$${moFile%.*}; \
	    $(mkdir) "$(DESTDIR)$(localedir)/$$lang/LC_MESSAGES"; \
	    cp $$moFile "$(DESTDIR)$(localedir)/$$lang/LC_MESSAGES/$(displayname).mo"; \
	done

uninstall:
	find "$(DESTDIR)$(localedir)" -name "$(displayname).mo" -exec rm {} ';'

                                                        