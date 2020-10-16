# Personal go links
If you've ever set foot in an office building in Silicon Valley, you may have noticed that the noticeboards, placards, cafe menus and occasionally even construction signs were plastered with a certain type of cryptic missive: `go/food`, you might have seen, or `go/hr`, perhaps even `go/home`. These ubiquitous strings are neither exclamations nor directives but in fact a highly useful kind of shortened URL: `go/food` could stand for `https://whatever.com/menu`, for instance, or `go/hr` could be `https://fizzbuzz.corp.com/human-resources`. Anyone inside the company can create a new go link with the name and URL of their choosing, and everything from meeting notes to slide decks to API docs have their own go links. You can type go links directly into the address bar of your browser, and they are highlighted automatically in commit descriptions, chat messages, bug comments, and the like.

I found go links to be useful enough at work that I wrote my own go links service for my personal computer. I have `go/weather` pointed at [Dark Sky](https://darksky.net/) and `go/air` at the EPA's [Air Quality Index page](https://www.airnow.gov/) for my city. `go/python/xyz` points to the Python standard library docs: `go/python/re` takes me to the documentation for the `re` package, `go/python/http` takes me to the `http` docs, and so on. I use another prefix, `gh/`, to go to my GitHub repositories: `gh/blog` brings up [the source code for my blog](https://github.com/iafisher/blog). The latter two kinds of links are especially useful because you could not feasibly make bookmarks for all the modules in the Python standard library, or all of your GitHub repositories.


## The code
The code for the go links service is very straightforward. It intercepts HTTP requests for go links using a Firefox extension, and sends them to a local server that looks up the link destination and sends an HTTP redirect back to the browser.

Here's the Firefox extension. It uses the [`webRequest`](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webRequest) API to intercept and redirect HTTP requests:

```js
function redirect(request) {
  const prefix = 'http://go/';
  const path = request.url.slice(prefix.length);
  return { redirectUrl: 'http://localhost:5000/go/' + path };
}

browser.webRequest.onBeforeRequest.addListener(redirect, { urls: ['http://go/*']}, ['blocking']);
```

If you use Chrome rather than Firefox, change `browser.webRequest` in the last line to `chrome.webRequest`.

And here's the server code. It uses [Flask](https://flask.palletsprojects.com/en/1.1.x/) for convenience, but the standard library [`http`](https://docs.python.org/3.6/library/http.html) module would also work:

```python
from flask import Flask, redirect

app = Flask(__name__)

LINKS = {
    "iafisher": "https://iafisher.com",
}

@app.route("/go/<path:path>")
def go(path):
    return redirect(LINKS[path])
```

If you have Flask [installed](https://flask.palletsprojects.com/en/1.1.x/installation/#installation), you can start the server with `export FLASK_APP=goserver.py; python3 -m flask run`, assuming the code is in a file called `goserver.py`.


## Installing the browser extension
To install the browser extension, create a file called `manifest.json` with the following contents:

```json
{
  "manifest_version": 2,
  "name": "GoLinks",
  "version": "0.1",
  "description": "Redirects http://go/ links to localhost:5000",
  "background": {
    "scripts": [
      "redirect.js"
    ]
  },
  "permissions": ["webRequest", "webRequestBlocking", "<all_urls>"]
}
```

Put the JavaScript code from above in a file called `redirect.js` alongside the manifest file.

### On Firefox
You can now install the extension on Firefox temporarily following [these instructions](https://extensionworkshop.com/documentation/develop/temporary-installation-in-firefox/). Unfortunately, Mozilla won't let you install the extension permanently without signing it on their servers. To do so, you will first need to [create API credentials](https://addons.mozilla.org/en-US/developers/addon/api/key/).

Once you have your API credentials, create a `.secrets` file outside[^why-outside] of the directory that holds `redirect.js` and `manifest.json` with:

```
export WEB_EXT_API_KEY=<your key here>
export WEB_EXT_API_SECRET=<your secret here>
```

Don't track this file in git, since it contains your secret key.

Finally, you'll need to use Mozilla's [`web-ext`](https://github.com/mozilla/web-ext) command-line tool to build and sign the extension. Install it with `npm install -g web-ext` and, inside the directory with your files, run:

```shell
web-ext build -o
source ../.secrets
web-ext sign
```

`web-ext sign` will take quite a while. When it's finished, you will have an `.xpi` file in a new `web-ext-artifacts` directory, which you can then install permanently from the about:addons page using the "Install Add-on From File" option. Note that each time you sign the extension, you'll need to bump the version number in the manifest.

Firefox tends to interpret go links as search queries rather than URLs, which bypasses the extension entirely and sends them straight to the search engine. You can fix this by going to `about:config` in Firefox and adding a new `browser.fixup.domainwhitelist.go` boolean setting, set to true. Or you can set `browser.fixup.dns_first_for_single_words`, in case you want to use multiple prefixes or a different one than `go/`.[^mozilla-bug]

### On Chrome
On Chrome, enter `chrome://extensions` in your address bar, turn on developer mode, click on "Load unpacked", and select the directory containing `manifest.json`. Your extension will remain installed even after you close the browser.


## Alternative approaches
You may wonder, is the local server even necessary? Why can't you just put the `LINKS` map in the extension and directly redirect requests that way?

The answer is, you could, but you would have to reload your extension every time you added a new link. Since, as we've seen, re-installing the extension takes some time, this wouldn't be practical unless you rarely or never add new links.

If you are hell-bent on avoiding a local server, you could try using the [persistent storage](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/storage) API to store the links in the extension, but that likely won't work, either. The problem is that the `storage.get` method is [asynchronous](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/storage/StorageArea/get), but the `redirect` function must be synchronous to be able to redirect the request. MDN [claims](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/webRequest/onBeforeRequest) that the `onBeforeRequest` callback can return a Promise, but I've found that you can't redirect the request with a Promise, and Promises [might not work at all](https://stackoverflow.com/questions/47910732/browserextension-webrequest-onbeforerequest-return-promise) in Chrome.

Another way you could do it is by setting `go` as an alias to an IP address of your choosing in your computer's [`hosts.txt`](https://en.wikipedia.org/wiki/Hosts_(file)). This would require you to either bind your local server to port 80 or spin up a server on the public Internet, but it would obviate the need for a browser extension.


## Prior art
[golinks.io](https://www.golinks.io) sells go links as a managed service. It's ostensibly free for individual users, but you need a company email address to sign up (i.e., not a Gmail address). You can manage links through a web interface, track the number of visits to each link, and control access to individual links, among other things.

According to [a Medium post published by golinks.io](https://medium.com/@golinks/the-full-history-of-go-links-and-the-golink-system-cbc6d2c8bb3), the go link was created at [North Carolina State University](https://golinks.ncsu.edu) in 2009, although their implementation (as of 2020) uses a dedicated `go.nscu.edu/` subdomain rather than the more concise `go/` domain.[^go-subdomain]

Go links were introduced to Google by [Benjamin Staffin](https://www.linkedin.com/in/benjaminstaffin), and former Googlers spread across the tech industry.

I found a couple of other personal go links projects on GitHub. Kelly Norton's [version](https://github.com/kellegous/go) is the most similar to mine. James Mills's [implementation](https://github.com/prologic/golinks) works by overriding the browser's default search engine, so you can enter `whatever` into your address bar instead of `go/whatever`. This is similar to [Facebook's internal system](http://www.bunny1.org/). Adam Yi's [version](https://github.com/adamyi/golinks) is a GCP project that binds to a custom domain, like at NCSU.


[^why-outside]: If you put it alongside your code, then `web-ext` will put it in the extension bundle and Mozilla will refuse to sign it on the grounds that it contains your secret key in plaintext.

[^mozilla-bug]: Thanks to [Marco Bonardo](https://bugzilla.mozilla.org/user_profile?user_id=240353) for pointing out this workaround on [Bugzilla](https://bugzilla.mozilla.org/show_bug.cgi?id=1642435).

[^go-subdomain]: And thus doesn't require any browser extension trickery to work: you can just bind a server to the subdomain and have it send redirects directly.
