# Why I am writing a new programming language
This summer, I have been working on a new programming language called Venice. Venice is modern, high-level, and statically-typed. It aims to combine the elegance and expressiveness of Python with the static typing and modern language features of Rust. When it is finished, it will look something like this:

```venice
import map, join from "itertools"

enum Json {
  JsonObject({string: Json}),
  JsonArray([Json]),
  JsonString(string),
  JsonNumber(real),
  JsonBoolean(bool),
  JsonNull,
}

func serialize_json(j: Json) -> string {
  match j {
    case JsonObject(obj) {
      let it = ("\(key): \(serialize_json(value))" for key, value in obj)
      return "{" ++ join(it, ", ") ++ "}"
    }
    case JsonArray(values) {
      return "[" ++ join(map(values, serialize_json), ", ") ++ "]"
    }
    case JsonString(s) {
      return s.quoted()
    }
    case JsonNumber(x) {
      return string(x)
    }
    case JsonBoolean(x) {
      return string(x)
    }
    case JsonNull {
      return "null"
    }
  }
}
```

At a minimum, Venice will include:

- Built-in list, map, and set types
- Structured data types (like structs in C, Rust, and Go)
- Algebraic data types and pattern matching
- Interface types
- A foreign-function interface
- Syntactic sugar like keyword and default function arguments, string interpolation, and list and map comprehensions
- A build system, code formatter, linter, and package manager

Why write a new programming language? For the past five years, Python has been my primary programming language, and in that time I have come to both appreciate its strengths and rue its weaknesses. The language is beginning to show its age: dynamic typing is no longer in vogue; algebraic data types, pattern matching, and non-nullable types, formerly confined to academia, are now mainstream; package managers have become ubiquitous; concurrency is no longer a niche feature. Still, no other language has come as close to my ideal as Python has. In Venice, I hope to take what I love about Python—its readability, expressiveness, and elegance—and combine it with what I love about other languages.

Detailed information about Venice is available in the [official tutorial](https://github.com/iafisher/venice/blob/master/docs/tutorial.md) and the [language reference](https://github.com/iafisher/venice/blob/master/docs/reference.md).[^under-development] If you are interested in Venice, please check out the project on [GitHub](https://github.com/iafisher/venice), and feel free to reach out to <a href="mailto:iafisher@fastmail.com">iafisher@fastmail.com</a> with any comments, questions, or suggestions about the language.


[^under-development]: Although note that since Venice is still in early development, not all of the language features described in those documents are available as of September 2021.
