# The technology behind a web app with 200,000 monthly visits
I operate [a collection of online geography quizzes](https://iafisher.com/projects/cities/quizzes) which challenge you to name as many cities, towns, and villages in a particular country or continent as you can, and which together see about 200,000 unique visits per month. The technology that allows me to run these quizzes by myself on a minimal budget is not especially remarkable, but it does demonstrate that a simple application architecture built on free, open-source software is more than sufficient for a moderately popular website.


## Backend
The site runs on a single [Digital Ocean](https://www.digitalocean.com) server with 1 GB of RAM and 25 GB of disk space. Despite its size, the server can achieve an impressive level of performance. In one recent surge, it handled 90 HTTP requests per second for an hour with a 95th percentile response time of 7 milliseconds while only using about 30% of its memory and CPU,[^response-time] which suggests that my monthly traffic could easily double without the physical hardware becoming a bottleneck.

The backend is written in Python using [the Django web framework](https://www.djangoproject.com). In front of Django sits [Gunicorn](https://gunicorn.org), which runs multiple Django instances in separate processes, and [Nginx](https://www.nginx.com), which delegates incoming HTTP requests from the outside world to Gunicorn and serves static assets (e.g., JavaScript, CSS, images).

The primary datastore is a [Postgres](https://www.postgresql.org) instance running on the same server. For convenience, I use [SQLite](https://sqlite.org/index.html) in development. Caching is done by [Redis](https://redis.io), also on the same server.

This set-up replaced a much more complex one on AWS that used [Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk) to manage the infrastructure. I had a load balancer in front of an auto-scaling group with a separate database server and an S3 bucket for my static assets, and an exact duplicate of everything in a staging environment. Eventually I realized that the fact that my auto-scaling group almost always contained only a single server was an indication that my infrastructure was excessive, and once my free tiers benefits expired and my monthly bill skyrocketed, I decided to switch to Digital Ocean.[^aws] By doing so I cut my costs to a quarter of what they were without affecting my site's performance.

For security, I followed most of the steps at ["My First 5 Minutes On A Server"](https://plusbryan.com/my-first-5-minutes-on-a-server-or-essential-security-for-linux-servers) by Bryan Kennedy. SSH access requires public-key authentication, and root log-in over SSH is disabled. [Fail2ban](https://www.fail2ban.org/wiki/index.php/Main_Page) monitors the Nginx logs for bad actors and blocks any that it finds.


## Frontend
The frontend is written in [TypeScript](https://www.typescriptlang.org) and bundled by [Webpack](https://webpack.js.org). Most of the user interface uses [Mithril](https://mithril.js.org), a lightweight React alternative. [D3](https://d3js.org) helps me render the maps and plot points for the geography quizzes, and the [`svg-pan-zoom`](https://github.com/ariutta/svg-pan-zoom) library handles zooming and panning in the SVG viewport.


## Deployment
One downside of moving from Elastic Beanstalk to Digital Ocean is that I became responsible for my own deployment and monitoring infrastruture.[^do-mon]

I deploy my site's code from my laptop to the staging server and then on to production using two shell scripts that I wrote myself: `upload` and `update`.[^hand-rolled] `upload` builds the frontend and then bundles every file in the git repository into a zip file and uploads it to the server. Once that is done, I connect to the server through SSH and run the `update` script. `update` initializes the new code in a timestamped directory, e.g. `/home/deploy/v2020-09-06-T-09-51-AM`. When initialization is finished, the symlink `/home/deploy/old` is pointed at the current directory and `/home/deploy/current` is pointed at the new one. This way, if any of the initialization steps fail then the server will continue to run the old code without a problem, and if the new code turns out to have a problem in production then switching back to the old code is as simple as changing `/home/deploy/current` to point to `/home/deploy/old`.

Configuration files for external applications (e.g., Nginx) are symlinked to master copies in `/home/deploy/current`, so that the `update` script will automatically apply any changes I make to the configuration. The script is uploaded to the server separately from the zipped application code so that I'm always running the latest version.


## Monitoring and analytics
To detect if the site is down, a script on the staging server runs every 15 minutes, tries a few production URLs, and sends me an SMS alert using [Twilio](https://www.twilio.com) if they cannot be reached.

I use [GoatCounter](https://www.goatcounter.com) for user analytics. Compared to Google Analytics, it is smaller (and thus loads more quickly on my pages) and doesn't track personal data.

For server-side analytics, a cron job runs every hour to aggregate statistics from the logs into a CSV file. The data in the CSV file is displayed as a set of graphs that are accessible on a password-protected dashboard on the site.

I have a special log file for "impossible" errors which are expected never to occur, and another file for errors that occur client-side, which are sent to the backend via a POST request to an API endpoint that logs the details so that I can identify and troubleshoot frontend issues in production.

Once a day, a cron job runs a database backup script that dumps the database to a text file using [`pg_dump`](https://www.postgresql.org/docs/11/app-pgdump.html) and uploads it to a Digital Ocean Spaces bucket. The script rotates the backups so that I always have full backups from the past 10 days.


## Testing
The bulk of my test suite are end-to-end tests that run on [Selenium](https://www.selenium.dev), a library that allows you to programmatically control a browser and simulate the actions of a real user. I have a fair number of unit tests, the majority of which are server-side tests using [Django's built-in testing framework](https://docs.djangoproject.com/en/3.1/topics/testing/). The frontend code is mainly covered by the Selenium tests, but I do have a small collection of TypeScript unit tests with [Mocha](https://mochajs.org) as the test framework and [Chai](https://www.chaijs.com) as the assertion library. I occasionally load-test the server with [Locust](https://locust.io). I use [my own pre-commit library](https://github.com/iafisher/precommit/) to run my unit tests as well as many other checks before each commit.


## Conclusion
My tech stack is not fancy. I do not use Kubernetes, microservices, Kafka or NoSQL. My database is not sharded. My static assets are not on a content-delivery network. For some, complicated infrastructure is undoubtedly justified. But I hope to have shown that you can run a moderately popular website with technology that is simple enough for a single developer to understand and afford.

If you enjoyed this post, you should also read Wenbin Fang's [excellent article](https://www.listennotes.com/blog/the-boring-technology-behind-a-one-person-23/) on the boring technology behind his one-person start-up, [Caspar von Wrede's write-up on running a Python web app for 55,000 monthly users](https://keepthescore.co/blog/posts/costs-of-running-webapp/), and Harry J. W. Percival's free online book [*Test-Driven Development with Python*](https://www.obeythetestinggoat.com), which covers building and deploying a Python web application.


[^response-time]: Measured as the time between Nginx forwarding a request to Django and receiving a response.

[^aws]: I could have stayed on AWS by moving from an Elastic Beanstalk environment to a single EC2 instance, but it would have required similar effort as migrating to Digital Ocean and I preferred Digital Ocean's user interface, documentation and billing.

[^do-mon]: Digital Ocean Droplets have some built-in monitoring, but they don't have web server-specific metrics like the number of requests per second, and they aren't able to detect if the web server is down but the Droplet is still running.

[^hand-rolled]: I wouldn't recommend doing deployments this way, and I'm exploring switching to a real framework like [Ansible](https://docs.ansible.com/ansible/latest/index.html), but for a hobby site that I work on in my free time, it's good enough for the time being.
