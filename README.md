# reimagined-pancake
Django app for running Your tests in a browser.

Caution
--
Becasue of how django runs tests(it modifies settings.py on the fly)
**it's not recommended** to use this app in production environment.

Installation
--

1. git clone
2. add `visualize` app to Your django project(add it to `INSTALLED_APPS`)
3. in settings.py set

        DEBUG=True

        ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
4. in `urls.py` include `visualize` urls:

        url(r'^tests/', include('visualizer.urls')),
5. Run server

URLs:
---

* `127.0.0.1:8000/tests/run/` : runs all tests
* `127.0.0.1:8000/tests/run/valid.path.to.django.tests.as.provided.to.manage.py` runs specified test

TODO:
--
* Styling and general HTML clean up
* Running individual tests from results page
* Grouping tests by app

Enjoy!