# wikiget

[![Build Status](https://travis-ci.org/clpo13/python-wikiget.svg?branch=master)](https://travis-ci.org/clpo13/python-wikiget)
[![PyPI version](https://badge.fury.io/py/wikiget.svg)](https://badge.fury.io/py/wikiget)

Something like wget for downloading a file from MediaWiki sites (like Wikipedia
or Wikimedia Commons) using only the file name or the URL of its description
page.

Requires Python 2.7 or 3.5+. Install with `pip install --user wikiget`.

## Usage

`wikiget [-h] [-V] [-q | -v] [-f] [--site SITE] [-o OUTPUT] FILE`

If `FILE` is in the form `File:Example.jpg` or `Example.jpg`, it will be fetched
from the default site, which is "en.wikipedia.org". If it's the fully-qualified
URL of a file description page, like `https://commons.wikimedia.org/wiki/File:Example.jpg`,
the file is fetched from the specified site, in this case "commons.wikimedia.org".
Full URLs may contain characters your shell interprets differently, so you can
either escape those characters with a backslash `\` or surround the entire URL
with single `'` or double `"` quotes.

The site can also be specified with the `--site` flag, though this will not have
any effect if the full URL is given.

More detailed information, such as the site used and full URL of the file, can be
displayed with `-v` or `--verbose`. Use `-vv` to display even more detail. `-q` can
be used to silence warnings.

By default, the program won't overwrite existing files with the same name as the
target, but this can be forced with `-f` or `--force`. Additionally, the file can
be downloaded to a different name with `-o`.

### Examples

```bash
wikiget File:Example.jpg
wikiget --site commons.wikimedia.org File:Example.jpg
wikiget https://en.wikipedia.org/wiki/File:Example.jpg -o test.jpg
```

## Future plans

- batch download categories, user uploads, or from a text file
- download from any MediaWiki-powered site, not just Wikimedia projects
- download Wikipedia articles, in plain text, wikitext, or other formats

## Contributing

It's recommended that you use a
[virtual environment manager](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
like venv or [virtualenv](https://virtualenv.pypa.io/en/latest/)) to
install dependencies:

```bash
git clone https://github.com/clpo13/python-wikiget.git
cd python-wikiget

# Python 2 or 3
pip install --user virtualenv
virtualenv venv

# Python 3
python3 -m venv venv
```

To activate the virtual environment, use one of the following commands:

```bash
source venv/bin/activate  # Linux and macOS
.\venv\Scripts\activate   # Windows
```

Then run `pip install -e .` to invoke an
["editable" install](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs),
meaning any changes made to the source will be reflected immediately in the
executable script. Unit tests can be run with `python setup.py test`.

## License

Copyright (C) 2018-2019 Cody Logan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (see [LICENSE](LICENSE)). If not, see
<https://www.gnu.org/licenses/>.
