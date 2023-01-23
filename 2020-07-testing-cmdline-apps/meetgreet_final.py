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
