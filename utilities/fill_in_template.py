import argparse
import sys
from pathlib import Path


def main(*, title, url):
    p = Path(__file__).absolute().parent

    txt_template = (p / "email_template.txt").read_text()
    txt_email = txt_template.replace("{{URL}}", url).replace("{{TITLE}}", title)
    print()
    print(txt_email)
    print()
    confirm()

    html_template = (p / "email_template.html").read_text()
    html_email = html_template.replace("{{URL}}", url).replace("{{TITLE}}", title)

    print()
    print(html_email)
    print()
    print("Copy-paste the above into Sendy.")


def confirm():
    while True:
        r = input("Continue? ").strip().lower()
        if r == "y" or r == "yes":
            return
        elif r == "n" or r == "no":
            print("Aborted.")
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url")
    parser.add_argument("--title")
    args = parser.parse_args()

    main(title=args.title, url=args.url)
