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
