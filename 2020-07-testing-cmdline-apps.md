# Testing command-line applications
I write a lot of command-line programs to make my life easier. Many of these are tiny scripts that I don't even bother tracking with git, but some, like [`oeuvre`](https://github.com/iafisher/oeuvre/) and [`drill`](https://github.com/iafisher/drill/), have grown into full-blown applications of thousands of lines of code with substantial test suites. Through trial and error, I've worked out a nice way of structuring my code so that end-to-end tests are easy to write even for highly interactive command-line programs.

To demonstrate the technique, let's consider a minimal example of an interactive program. Our example program simply meets and greets its users:

```
$ python3 meetgreet.py greet
Hello!

$ python3 meetgreet.py meet
Hello, what's your name? Ian
Nice to meet you, Ian!
```

Without thinking about testing, I'd write the program like this:[^language]

```python
import sys

def main(args):
    if not len(args) == 1:
        print("error: expected exactly one command-line argument", file=sys.stderr)
        sys.exit(1)

    if args[0] == "meet":
        main_meet(args)
    elif args[0] == "greet":
        main_greet(args)
    else:
        print(f"error: unknown subcommand: {args[0]}", file=sys.stderr)
        sys.exit(1)

def main_meet(args):
    name = input("Hello, what's your name? ")
    name = name.strip()
    print(f"Nice to meet you, {name}!")

def main_greet(args):
    print("Hello!")

if __name__ == "__main__":
    main(sys.argv[1:])
```

The code is straightforward, but it's not very easy to test end-to-end, because it has hard-coded implicit dependencies on standard input and output by virtue of using the `print` and `input` standard library functions. To test the applicaton, you would have to use the `patch` function from [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) to patch the standard I/O streams (e.g., using `io.StringIO` buffers), but this has a couple of downsides. Since patching replaces the I/O streams globally for the code under test, you can no longer use `print` statements to troubleshoot your tests,[^patch-print] and you can't use `pdb` for debugging tests because its interactive shell uses standard input.

To make the code more testable, let's put all of our UI logic into an `Application` class which takes explicit parameters for output, error and input streams. In our `if __name__ == "__main__"` block, we'll instantiate an `Application` object with the normal I/O streams, but in our tests, we'll pass fake streams instead. We'll also define three convenience methods on the `Application` class: `print`, `error` and `input`.

```python
import sys

class Application:
    def __init__(self, *, stdout, stderr, stdin):
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin

    def main(self, args):
        if not len(args) == 1:
            self.error("error: expected exactly one command-line argument")

        if args[0] == "meet":
            self.main_meet(args)
        elif args[0] == "greet":
            self.main_greet(args)
        else:
            self.error(f"error: unknown subcommand: {args[0]}")

    def main_meet(self, args):
        name = self.input("Hello, what's your name? ")
        name = name.strip()
        self.print(f"Nice to meet you, {name}!")

    def main_greet(self, args):
        self.print("Hello!")

    def print(self, *args, **kwargs):
        print(*args, **kwargs, file=self.stdout)

    def error(self, *args, **kwargs):
        print(*args, **kwargs, file=self.stderr)
        sys.exit(1)

    def input(self, prompt):
        print(prompt, end="", flush=True, file=self.stdout)
        return self.stdin.readline()

if __name__ == "__main__":
    app = Application(stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
    app.main(sys.argv[1:])
```

Now that we've restructured our application code, writing end-to-end tests is a breeze:

```python
import unittest
from io import StringIO

from meetgreet_final import Application

class MeetGreetTests(unittest.TestCase):
    def test_meet(self):
        stdout = StringIO()
        # Simulate entering 'Ian' at the prompt.
        stdin = StringIO("Ian\n")
        app = Application(stdout=stdout, stderr=None, stdin=stdin)

        app.main(["meet"])

        self.assertEqual(
            stdout.getvalue(), "Hello, what's your name? " + "Nice to meet you, Ian!\n"
        )

    def test_greet(self):
        stdout = StringIO()
        app = Application(stdout=stdout, stderr=None, stdin=None)

        app.main(["greet"])

        self.assertEqual(stdout.getvalue(), "Hello!\n")

if __name__ == "__main__":
    unittest.main()
```

Since we're not patching anything, we're free to use `print` statements in our code or `pdb` for debugging.

In summary, to write easily testable command-line applications, you should:

- Encapsulate all of the UI logic in a single `Application` class.

- Avoid functions like `print` and `input`. Instead, accept standard output and input streams as parameters to the `Application` constructor and use these stream objects whenever you want to print something or accept user input.

According to the [conventional wisdom](https://martinfowler.com/articles/practical-test-pyramid.html), most tests should be unit tests and only a few tests should be full end-to-end tests. Personally, for small command-line applications I find that end-to-end tests bring more value without much extra cost (`oeuvre`'s suite of 16 end-to-end tests runs in under a tenth of a second), but regardless, for the end-to-end tests that you do have, a simple logical structure for your application makes writing them much easier.


[^language]: The example is in Python, but the principles are language-independent.

[^patch-print]: You technically still can, but it's harder because your debugging output is captured in the string buffer with everything else.
