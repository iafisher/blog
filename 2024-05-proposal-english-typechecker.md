# Proposal: A type-checker for English prose
I would like to have a command-line tool that checks the *grammatical correctness* of English-language prose. Such a tool could be run on code documentation as part of a pre-commit pipeline, on blog posts before publication, or anywhere else that the automated checking of English grammar is desirable. What I have in mind has a similar interface to [Vale](https://vale.sh/), but while Vale is a *linter* that catches *stylistic* errors, I want a *type-checker* that catches *grammatical* errors.[^1]

I believe that the best way to write such a tool is using a rule-based approach – meaning that it will have pre-programmed and explicit knowledge of English grammar. Let's call this a *rules engine*.

The alternative would be a machine-learning model that classifies sentences as grammatical or ungrammatical. In 2024, machine learning is perhaps the more obvious choice, but I think a rules engine is more appropriate, for two reasons:

- *Error rate*: A type-checker must make few mistakes to be useful. If a grammar checker constantly gives spurious errors, I will simply stop using it. This is unlike other machine-learning tasks like speech processing or optical character recognition, where a reasonably low error rate is tolerable. A "rules engine" is really just a regular program, and bugs can be fixed by editing the code; but a machine-learning algorithm is an opaque blob of numeric parameters, and fixing individual errors may be difficult or impossible.
- *Interpretability*: The grammar checker needs to report *why* it thinks a sentence is incorrect. A rules engine can be programmed to produce helpful error messages, but a machine-learning model's reasoning is opaque and not easily interpreted.

I'm open to using statistical methods for subsystems of the grammar checker, but I suspect it will be easier to embed them within the rules engine than to retrofit formal rules onto a statistical system.

I am aware that this goes against the [orthodoxy](https://norvig.com/chomsky.html), so let me respond preemptively to some possible objections:

*Formal rules don't work for natural-language processing; experience has shown that statistical methods are always better*. This may well turn out to be the case, but as I've outlined above, I have good pragmatic reasons to favor my approach.

*Real natural-language prose is too flexible for a formal grammar.* First, to clarify, I'm proposing to write a program, not a grammar. I'm under no illusions that English can be parsed with a tidy formalism like a context-free grammar. Second, my goal is to check the grammatical correctness of (relatively) formal, written English. Colloquial speech, literary writing, dialogue etc. are out of scope. I think that this constrains the problem enough that it is realistically solvable – but it might turn out that it's impossible to thread the needle between "it's too permissive and misses too many mistakes" and "it's too strict and disallows too many correct sentences."

*Grammaticality isn't a binary. Some sentences are "borderline", or might be grammatical or not depending on context.* This is probably true, but may not be important in practice. I suspect that many borderline sentences are inappropriate in formal writing even if they are technically grammatical.

*Parsing the syntax of a natural language is computationally intractable.* Again, this might be theoretically true, but my wager is that if I approach the problem with an *engineering* mindset rather than an *academic one*, then theoretical difficulties may prove to be surmountable.

*Full syntactic analysis requires semantic analysis.* For instance, a typo might produce a rare word that is syntactically valid but semantically nonsensical, and the only way to detect such an error would be to understand the meaning of the sentence. Cases like these are good candidates for integrating statistical methods into the rules engine.

It's possible that some or all of these objections will turn out to be valid. But the only way to know for sure is to try.

At the time of writing (May 2024), I'm doing a coding retreat at [Recurse Center](https://recurse.com). I plan to set aside some time to work on this project, so expect more blog posts in the near future.

If you read this post and you think I'm wrong, please send me an email at \<my name> @ \<this domain name>. I'd be happy to hear about it.

[^1]: Vale also catches some grammatical and spelling errors, but fundamentally it is a tool for matching style rules to text, not for comprehensive grammatical analysis.
