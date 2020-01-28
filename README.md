# wikiget

[![Build Status](https://travis-ci.org/clpo13/wikiget.svg?branch=master)](https://travis-ci.org/clpo13/wikiget)
[![PyPI version](https://badge.fury.io/py/wikiget.svg)](https://badge.fury.io/py/wikiget)

Something like wget for downloading a file from MediaWiki sites (like Wikipedia
or Wikimedia Commons) using only the file name or the URL of its description
page.

Requires Python 3.5+. Get it with `pip install --user wikiget` or, if you prefer
[Homebrew](https://brew.sh/), `brew tap clpo13/brew && brew install wikiget`.

## Usage

`wikiget [-h] [-V] [-q | -v] [-f] [--site SITE] [-o OUTPUT | -a] FILE`

If `FILE` is in the form `File:Example.jpg` or `Example.jpg`, it will be fetched
from the default site, which is "commons.wikimedia.org". If it's the
fully-qualified URL of a file description page, like
`https://en.wikipedia.org/wiki/File:Example.jpg`, the file is fetched from the
specified site, in this case "en.wikipedia.org".  Full URLs may contain
characters your shell interprets differently, so you can either escape those
characters with a backslash `\` or surround the entire URL with single `'` or
double `"` quotes.

The site can also be specified with the `--site` flag, though this will not have
any effect if the full URL is given.

More detailed information, such as the site used and full URL of the file, can
be displayed with `-v` or `--verbose`. Use `-vv` to display even more detail.
`-q` can be used to silence warnings.

By default, the program won't overwrite existing files with the same name as the
target, but this can be forced with `-f` or `--force`. Additionally, the file
can be downloaded to a different name with `-o`.

Files can be batch downloaded with the `-a` or `--batch` flag. In this mode,
`FILE` will be treated as an input file containing multiple files to download,
one filename or URL per line. If an error is encountered, execution stops
immediately and the offending filename is printed.

### Example usage

```bash
wikiget File:Example.jpg
wikiget --site en.wikipedia.org File:Example.jpg
wikiget https://en.wikipedia.org/wiki/File:Example.jpg -o test.jpg
```

## Future plans

- continue batch download even if input is malformed or file doesn't exist
  (possibly by raising exceptions in `download()`)
- batch download by (Commons) category or user uploads
- download from any MediaWiki-powered site, not just Wikimedia projects
- maybe: download Wikipedia articles, in plain text, wikitext, or other formats

## Contributing

It's recommended that you use a
[virtual environment manager](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
like venv or [virtualenv](https://virtualenv.pypa.io/en/latest/) to create an
isolated environment in which to install this package's dependencies so as not
to clutter your system Python environment:

```bash
# if you plan on submitting pull requests, fork the repo on GitHub
# and clone that instead
git clone https://github.com/clpo13/wikiget
cd wikiget
python3 -m venv venv
```

To activate the virtual environment, use one of the following commands:

```bash
# Linux and macOS; activate.csh and activate.fish are also available
source venv/bin/activate

# Windows (Command Prompt or PowerShell)
.\venv\Scripts\activate
```

Then run `pip install -e .` to invoke an
["editable" install](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs),
meaning any changes made to the source will be reflected immediately in the
executable script. Unit tests can be run with `python setup.py test`.

## License

Copyright (C) 2018, 2019, 2020 Cody Logan

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
