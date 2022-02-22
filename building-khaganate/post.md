# Building Khaganate
[Last week's blog post](https://iafisher.com/blog/2022/02/khaganate) described Khaganate, my suite of personal productivity software. This post is a brief follow-up about the tools and technologies I used to build Khaganate.

Khaganate is intended to make me *more* productive, so it is important that development is as fast as possible. I lean heavily on three frameworks:

- [Django](https://www.djangoproject.com/), for the backend
- [Vue](https://vuejs.org/), for the frontend
- [Bootstrap Vue](https://bootstrap-vue.org/), to extend Vue with a library of high-quality components

Each of them is powerful and easy to use, and (equally as important) has great online documentation.

I've supplemented these frameworks with Khaganate-specific code to make development even faster.

I wrote a [set of generic database APIs](https://github.com/iafisher/khaganate-snapshot/blob/master/server/api_database.py) like `/api/db/get/<table>` that the frontend calls to interact directly with the database, saving me the need to write dozens of cookie-cutter CRUD endpoints for all the different database tables. Sometimes I can implement entire new features without having to make any changes to the backend. The database APIs are powered by the [isqlite](https://isqlite.readthedocs.io/en/latest/) library, which I wrote for use by Khaganate.

I often need to call the same code in JavaScript and in Python. I wrote a [decorator](https://github.com/iafisher/khaganate-snapshot/blob/master/server/adapter.py#L10) that transforms a Python function into a Django view so that the function can be exposed as a JSON API with minimal extra effort. The decorator handles JSON serialization and deserialization, conversion between snake case and camel case, and POST payloads and URL parameters. It also enforces that the database connection for GET requests is set to read-only.

On the frontend, I wrote a [`LoadingBox`](https://github.com/iafisher/khaganate-snapshot/blob/master/frontend/components/LoadingBox.vue) Vue component that fetches data from a backend API, displays a loading icon, and optionally refreshes the page upon request. This makes intricate interactions on the home page simple: when I log a habit, for example, the habit box component emits an event for the root home page component to catch, which then increments a refresh counter that is passed to the goals box component, causing it to refresh its data. As a result, when I log a habit that is tracked by a goal, the goal updates instantly.

A generic [`ModalForm`](https://github.com/iafisher/khaganate-snapshot/blob/master/frontend/components/ModalForm.vue) component makes it easy to embed modal forms for any kind of data. It takes a parameter describing the fields of the form, and handles rendering, validation, and submission.

Vue components call backend APIs using the [`ApiService`](https://github.com/iafisher/khaganate-snapshot/blob/master/frontend/services/api_service.js). The `ApiService` deserializes the response, handles the cross-site request forgery token, and shows a pop-up error message if the HTTP request fails. It also prints the full response to the browser console, which is very useful for after-the-fact debugging.

It is not specific to Khaganate, but the [`precommit`](https://github.com/iafisher/precommit) library that I wrote to manage Git pre-commit hooks has proven invaluable in catching errors and enforcing code style. I also have a Git review page within Khaganate, triggered by invoking the script `kgx review`, which shows the staged changes as GitHub-style diffs; I use it for self-reviewing my code.

I recognize the humor of writing productivity tools to make the development of my productivity software more productive. But the effort has paid off. Last month I wrote an entire new goals system in less than an hour and 200 lines of code. My life changes, sometimes quickly, and my tools must keep up.
