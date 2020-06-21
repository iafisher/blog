# A tool to manage git pre-commit hooks
I use [git pre-commit hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) in all my projects to ensure that my code meets some basic standards before I commit it. A pre-commit hook is a script at a special location (`.git/hooks/pre-commit`) that git will run whenever you try to make a commit. If the script exits with an error code, then git will abort the commit.

Here is a simple pre-commit hook for a Python project. It runs [`black`](https://black.readthedocs.io/en/stable/) (a Python code formatter), [`flake8`](https://pypi.org/project/flake8/) (a Python linter), and the project's test suite:

```shell
#!/bin/bash

set -e

black --check .
flake8 .
python3 tests.py
```

Simple as it is, this script has a couple of problems:

- It checks every Python file in the directory, including files that aren't tracked by git at all (e.g., files inside a virtual environment), files that haven't been modified since the last commit, and files that have been modified but have not been staged. This is highly inefficient, and doesn't allow for any files to be exempt from any of the checks.

- It exits as soon as any of the checks fail. You may want to run all the checks to see all the errors.

We can at least exclude non-Python files and files in the virtual environment (assuming that it is at `.venv`):

```shell
#!/bin/bash

set -e

PY=$(find . -path ./.venv -prune -o -name "*.py" -print)
black --check $PY
flake8 $PY
pytest
```

But we haven't fully solved the first problem, nor addressed the second problem at all, and our solution would quickly become unwieldy if we wanted checks for multiple languages.[^shell-whitespace]

Because these issues plagued me whenever I started a new project and discouraged me from writing more comprehensive pre-commit checks, I created my own tool, [`precommit`](https://github.com/iafisher/precommit), to manage my pre-commit hooks.

Above all, precommit is designed to be lightweight. To set up a pre-commit hook, you run `precommit init` anywhere in your git repository, which creates a configuration file called `precommit.py` in the repository's root and symlinks it to git's hooks directory. Then, the check will be triggered automatically whenever you run `git commit`. You can also trigger it manually with `precommit`.

Here's what it looks like:[^demo-credits]

<img src="/static/blog/uploads/precommit.svg">

The default configuration comes with a number of useful checks out of the box:[^install]

```python
from precommitlib import checks


def init(precommit):
    precommit.check(checks.NoStagedAndUnstagedChanges())
    precommit.check(checks.NoWhitespaceInFilePath())
    precommit.check(checks.DoNotSubmit())

    # Check Python format with black.
    precommit.check(checks.PythonFormat())

    # Lint Python code with flake8.
    precommit.check(checks.PythonLint())

    # Check the order of Python imports with isort.
    precommit.check(checks.PythonImportOrder())

    # Check Python static type annotations with mypy.
    # precommit.check(checks.PythonTypes())

    # Lint JavaScript code with ESLint.
    precommit.check(checks.JavaScriptLint())

    # Check Rust format with rustfmt.
    precommit.check(checks.RustFormat())
```

Most of the checks are enabled by default. There is no overhead for enabling checks in a language your project does not use, because checks are only run when a matching file is staged for the commit.

Many checks can fix problems as well as identify them. For example, `PythonFormat` can use `black` to automatically re-format your code, and `PythonImportOrder` can use `isort` to sort imports. To apply all available fixes, run `precommit fix`. You can pass `--working` to `precommit` and `precommit fix` to operate on both unstaged and staged changes.

If the built-in checks aren't enough, you can easily write your own checks with the `checks.Command` class:

```python
from precommitlib import checks


def init(precommit):
    # ...

    precommit.check(checks.Command("UnitTests", ["./test"]))
    precommit.check(checks.Command("GoFormat", ["gofmt"], pass_files=True, include=["*.go"]))
```

The first check, `UnitTests` runs a shell command (`./test`) with no arguments. The second check, `GoFormat`, runs `gofmt` on all staged files (`pass_files=True`) that match the given list of patterns (`include=["*.go"]`). Naturally, there is also an `exclude` parameter to exempt files from a check.

If this post has piqued your interest, you are welcome to fork your own version of precommit [on GitHub](https://github.com/iafisher/precommit). I encourage you to fork it rather than download it so that you can tailor it to your personal workflow and preferences. I've intentionally kept the tool small and only implemented the features that I need, which are likely not exactly the features that you need.

If you do just want to download it, you can do so with pip:

```shell
pip3 install git+https://github.com/iafisher/precommit.git
```

Note that depending on your system's configuration, pip may not place the `precommit` script on your `PATH`.


[^shell-whitespace]: We'd also need to adjust the `find` command to something like `find . -path ./.venv -prune -o -name "*.py" -print0 | xargs -0 black --check` in order to correctly handle file names that contain whitespace.

[^demo-credits]: The animation was created with [`termtosvg`](https://github.com/nbedos/termtosvg).

[^install]: Note that many of these checks require an external program (`black`, `flake8`, etc.) to be installed. precommit does not install them for you.
