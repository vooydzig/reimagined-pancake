from django.shortcuts import render_to_response

from .testrunner import DjangoHtmlTestRunner


def run_tests(request, test_path=None):
    if not test_path:
        from testhtml.settings import INSTALLED_APPS
        d = DjangoHtmlTestRunner().run_tests(INSTALLED_APPS)
    else:
        d = DjangoHtmlTestRunner().run_tests([test_path])
    return render_to_response('report.html', {'path': test_path,
                                              'results': dict(d),
                                              'global': d['global']})
