PREFIX ?= /usr/local

install:
	python3 setup.py install --root="$(DESTDIR)/" --prefix="$(PREFIX)"
	install -Dm644 conf/config $(DESTDIR)/$(PREFIX)/share/drys/config
	install -Dm644 extra/fish/vendor_completions.d/*.fish -t $(DESTDIR)/$(PREFIX)/share/fish/vendor_completions.d
