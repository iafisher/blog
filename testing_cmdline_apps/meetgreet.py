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
