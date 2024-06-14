# Automated grammar checking: existing tools
[My last post](https://iafisher.com/blog/2024/05/proposal-english-typechecker) proposed a command-line program to automatically check that a written text is grammatically correct – in software engineering terms, a "type-checker" for English prose. I further proposed that such a program should be *rule-based* rather than statistical.

Before embarking on writing such a program myself, I tried out the grammar checkers that already exist. These are my findings. The one-sentence summary is that I could not find an existing tool that meets my requirements. For the details, read on.

## Test sentences
I used four ungrammatical sentences to test existing tools:

1. One thing I am enthusiastic about tutoring.
	- Missing 'is' after 'about'
2. A one-on-one session is some of the best ways to help.
	- 'some of' should be 'one of'
3. Rust has excellent support for co-routines, which we are being actively developing.
	- 'we are being' should be 'we are'
4. We chose this particular algorithms since it is both work-conserving and has a special mechanism for low-latency wake-up of a domain when it receives an event.
	- 'algorithms' should be 'algorithm'

I either made these typos myself, or spotted them in published text.

\#1 is potentially tricky to catch because the substring on its own ("I am enthusiastic about tutoring") is correct. #2 is an example of more complicated subject–object agreement. #3 and #4 are simpler mistakes (auxiliary verb agreement, 'this' vs. 'these') but have some intervening words which could confuse simplistic checkers. #3 is more challenging to correct because the obvious substitution, 'developed' for 'developing', is incompatible with the 'which' at the beginning of the clause.

This is far from an exhaustive test. But I do think it is enough to get a rough impression of how good a grammar checker is.

## Existing tools
I ran the test sentences through 8 grammar-checking tools.

Detection:

| Tool                       | #1  | #2  | #3  | #4  |
| -------------------------- | --- | --- | --- | --- |
| Grammarly                  | yes | no  | yes | yes |
| ProWritingAid              | yes | no  | no  | no  |
| Ginger                     | no  | no  | yes | yes |
| LanguageTool (online)      | yes | yes | yes | yes |
| LanguageTool (open-source) | no  | no  | no  | no  |
| Google Docs                | no  | no  | yes | yes |
| Microsoft Word             | no  | no  | no  | yes |
| Vale                       | no  | no  | no  | no  |

Correction (left blank if it did not detect the error in the first place):

| Tool                       | #1  | #2  | #3  | #4  |
| -------------------------- | --- | --- | --- | --- |
| Grammarly                  | yes |     | yes | no  |
| ProWritingAid              | yes |     |     |     |
| Ginger                     |     |     | no  | yes |
| LanguageTool (online)      | yes | yes | yes | yes |
| LanguageTool (open-source) |     |     |     |     |
| Google Docs                |     |     | yes | yes |
| Microsoft Word             |     |     |     | yes |
| Vale                       |     |     |     |     |

[Grammarly](https://grammarly.com),  [ProWritingAid](https://prowritingaid.com/), [Ginger Proofreading](https://www.gingersoftware.com/proofreading) and the online version of [LanguageTool](https://languagetool.org/) are all proprietary commercial services, so they wouldn't work for my purposes, but I included them in the comparison anyway. The subset of LanguageTool's engine that is available as free software is listed separately. It powers [ltex-ls](https://valentjn.github.io/ltex/index.html) and [Gramma](https://caderek.github.io/gramma/). Google Docs and Microsoft Word have built-in grammar checkers. [Vale](https://vale.sh/) is more of a style checker than a grammar checker, but it's the closest existing tool to what I envision.

I excluded a couple of JavaScript tools similar to Vale – [TextLint](https://github.com/textlint/textlint), [rousseau](https://github.com/GitbookIO/rousseau), [write-good](https://github.com/btford/write-good) – which were either focused on style or used simplistic regular-expression matching that is inadequate for serious grammar-checking.

Grammarly and LanguageTool's online version did the best. Unfortunately, neither the open-source version of LanguageTool nor Vale caught any of the errors.

I was a little disappointed that Microsoft Word only caught one, as it is the "only publicly well-documented commercial-grade grammar-based syntax checker" (Dale & Viethen 2021) – that is, the same approach that I am pursuing, based on a full parse of the text rather than pattern-matching against a list of known errors, which is what LanguageTool does (Naber 2003; Mozgovoy 2011).

## Academic research
As my proposed design is a syntactic analyzer, I mainly read about computational grammars of natural languages, i.e. software that can parse sentences of natural language.

There have been several long-running *grammar engineering* projects that aim to create broad-coverage grammars of natural languages. One of the most complete is the [English Resource Grammar](https://github.com/delph-in/docs/wiki/ErgTop) (ERG), which is based on the theoretical formalisms of Head-Driven Phrase Structure Grammar (HPSG) and Minimal Recursion Semantics. It includes a wealth of information about English in machine-readable form: 35,000 lexemes, 980 lexical types, 70 inflectional rules, and 200 syntactic rules (Flickinger 2010). It also has [an online demo](https://delph-in.github.io/delphin-viz/demo/#input=hello%20there!&count=5&grammar=erg2018-uw&mrs=true). If you try it out, you'll quickly find that its analysis is at a level of detail that is probably unnecessary for the purpose of error detection. It is also – either by design or by accident – quite permissive: it produced a result for 3 of my 4 test sentences.

The Parallel Grammar Project (ParGram) is another grammar-engineering effort based on Lexical-Functional Grammar (LFG) rather than HPSG (Butt et al 2002).

On a different note, it would be helpful to have a large set of examples of ungrammatical sentences for testing and evaluation. The [Corpus of Linguistic Acceptability](https://nyu-mll.github.io/CoLA/) (CoLA) is just such a collection, drawn from published linguistic papers. Many of the ungrammatical sentences are meant to illustrate or test a particular academic theory, though, so they are not very representative of mistakes that people make in real life.

## Summary
There are many existing tools but none that meets my needs. The performance of some of the commercial products, Grammarly and LanguageTool's online version in particular, was impressive. The open-source tools did not come close.

The academic research into grammar engineering could be helpful. I don't think I could incorporate the ERG wholesale into my tool, but I might be able to extract and reuse some of the linguistic information inside of it.

I may yet be dissuaded, but for now I'm carrying on with my original plan: to write my own, open-source, rule-based grammar-checking tool.

As before, if you read this post and you think I'm wrong, please send me an email at `<my first name> @ <this domain name>`. I'd be happy to hear about it.

## Acknowledgements
Thank you to [Chris Mischaikow](https://github.com/mischaikow) and a person who wished to remain anonymous for running my test sentences through Microsoft Word and `ltex-ls`, respectively.

## Bibliography
- Butt et al 2002: "The Parallel Grammar Project" by Miriam Butt, Helge Dyvik, Tracy Holloway King, Hiroshi Masuichi, and Christian Rohrer, 2002. In *COLING-02: Grammar Engineering and Evaluation*. <https://aclanthology.org/W02-1503/>
- Dale & Viethen 2021: "The automated writing assistance landscape in 2021" by Robert Dale and Jette Viethen, 2021. In *Natural Language Engineering* 27, pp. 511–518. <https://doi.org/10.1017/S1351324921000164>
- Flickinger 2010: "Accuracy vs. Robustness in Grammar Engineering" by Dan Flickinger, 2010. In *Readings in Cognitive Science: Papers in Honor of Tom Wasow* edited by Emily M. Bender and Jennifer Arnold.
- Mozgovoy 2011: "Dependency-Based Rules for Grammar Checking with LanguageTool" by Maxim Mozgovoy, 2011. In *Proceedings of the Federated Conference on Computer Science and Information Systems*, pp. 209–212. ISBN 978-83-60810-22-4. <https://annals-csis.org/proceedings/2011/pliks/14.pdf>
- Naber 2003: "A Rule-Based Style and Grammar Checker" by Daniel Naber, 2003. Dissertation at Universität Bielefeld. <https://www.danielnaber.de/languagetool/download/style_and_grammar_checker.pdf>
- Omelianchuk et al 2020: "GECToR -- Grammatical Error Correction: Tag, Not Rewrite" by Kostiantyn Omelianchuk, Vitaliy Atrasevych, Artem Chernodub, and Oleksandr Skurzhanskyi, 2020. <https://arxiv.org/abs/2005.12592>
