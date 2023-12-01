# Contributing to wikiget

Pull requests, bug reports, or feature requests are more than welcome.

It's recommended that you use a [virtual environment manager][venv] like venv or [virtualenv] to create an isolated
environment in which to install this package's dependencies as not to clutter your system Python environment:

```bash
# if you plan on submitting pull requests, fork the repo on GitHub and clone that instead
git clone https://github.com/clpo13/wikiget
cd wikiget

python3 -m venv venv
# or
virtualenv venv
```

To activate the virtual environment, use one of the following commands:

```bash
# Linux and macOS; activate.csh and activate.fish are also available
source venv/bin/activate

# Windows (Command Prompt or PowerShell)
.\venv\Scripts\activate
```

Then run `pip install -e .` to invoke an ["editable" install][editable], meaning any changes made to the source will be
reflected immediately in the executable script. Unit tests can be run with `pytest` (make sure to run
`pip install pytest` in the virtual environment first.)

Alternatively, using [Hatch], simply clone the repository and run `hatch run test` to create the environment and run
pytest all in one go. Wikiget can also be run directly in the Hatch environment with `hatch run wikiget [...]`.

[venv]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[editable]: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
[hatch]: https://hatch.pypa.io/latest/
