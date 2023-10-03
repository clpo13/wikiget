% WIKIGET(1) Version 0.5.1 | Wikiget User Manual
% Cody Logan <clpo13@gmail.com>
% October 3, 2023

# NAME

wikiget - download files from MediaWiki sites

# SYNOPSIS

| **wikiget** \[*options*] *FILE*
| **wikiget** \[*options*] \[\-**a**|\-\-**batch**] *BATCHFILE*
| **wikiget** \[\-**V**|\-\-**version**]
| **wikiget** \[\-**h**|\-\-**help**]

# DESCRIPTION

Something like **wget**(1) for downloading a file from MediaWiki sites (like Wikipedia or Wikimedia Commons) using only
the file name or the URL of its description page.

# OPTIONS

*FILE*

:   The file to be downloaded. If *FILE* is in the form *File:Example.jpg* or *Image:Example.jpg*, it will be fetched
    from the default site, which is "commons.wikimedia.org". If it's the fully-qualified URL of a file description page,
    like *https://en.wikipedia.org/wiki/File:Example.jpg*, the file is fetched from the site in the URL, in this case
    "en.wikipedia.org".

*BATCHFILE*

:   In batch download mode (activated with \-**a** or \-\-**batch**), this is a text file containing multiple file names
    or URLs to be downloaded, one per line. If an error is encountered during download, execution stops immediately and
    the offending filename is printed.

\-**s**, \-\-**site** *SITE*

:   MediaWiki site to download from. Will not have any effect if the full URL is given in the *FILE* parameter.

\-**P**, \-\-**path** *PATH*

:   Script path for the wiki, where "index.php" and "api.php" live. On Wikimedia sites, it's "/w/", the default, but
    other sites may use "/" or something else entirely.

\-**u**, \-\-**username** *USERNAME*

:   Username for private wikis that require a login even for read access.

\-**p**, \-\-**password** *PASSWORD*

:   Password for private wikis that require a login even for read access.

\-**o**, \-\-**output** *OUTPUT*

:   By default, the output filename is the same as the remote filename (without the File: or Image: prefix), but this
    can be changed with this option.

\-**l**, \-\-**logfile** *LOGFILE*

:   Specify a logfile, which will contain detailed information about the download process. If the logfile already
    exists, new log information is appended to it.

\-**f**, \-\-**force**

:   Force existing files to be overwritten.

\-**a**, \-\-**batch**

:   If this flag is set, **wikiget** will run in batch download mode (see *BATCHFILE*).

\-**v**, \-\-**verbose**

:   Print additional information, such as the site used and the full URL of the file. Additional invocations will
    increase the level of detail.

\-**q**, \-\-**quiet**

:   Silence warnings and minimize printed output.

\-**h**, \-\-**help**

:   Print a brief summary of these options.

# EXAMPLES

```
wikiget File:Example.jpg
wikiget --site en.wikipedia.org File:Example.jpg
wikiget https://en.wikipedia.org/wiki/File:Example.jpg -o test.jpg
```

# BUG REPORTS

https://github.com/clpo13/wikiget/issues

# LICENSE

Copyright (C) 2018-2023 Cody Logan and contributors

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see
https://www.gnu.org/licenses/.
