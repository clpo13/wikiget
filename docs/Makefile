.PHONY: man

man: wikiget.1

wikiget.1: wikiget.1.md
	pandoc -s -f markdown -t man -o wikiget.1 wikiget.1.md
