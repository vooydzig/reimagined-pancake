import sys
import time
import unittest
import warnings
from collections import defaultdict
from django.test.runner import DiscoverRunner
from django.test.utils import teardown_test_environment, setup_test_environment


class DictTestResult(unittest.result.TestResult):
    def __init__(self, stream, descriptions, verbosity):
        super(DictTestResult, self).__init__(stream, descriptions, verbosity)
        self.descriptions = descriptions
        self.results = defaultdict(dict)

    def get_description(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def startTest(self, test):
        super(DictTestResult, self).startTest(test)
        self.results[str(test)].update({'description': self.get_description(test)})

    def addSuccess(self, test):
        super(DictTestResult, self).addSuccess(test)
        self.results[str(test)].update({'status': 'ok'})

    def addError(self, test, err):
        super(DictTestResult, self).addError(test, err)
        self.results[str(test)].update({'status': 'error'})

    def addFailure(self, test, err):
        super(DictTestResult, self).addFailure(test, err)
        self.results[str(test)].update({'status': 'fail'})

    def addSkip(self, test, reason):
        super(DictTestResult, self).addSkip(test, reason)
        self.results[str(test)].update({'status': 'skip', 'reason': reason})

    def addExpectedFailure(self, test, err):
        super(DictTestResult, self).addExpectedFailure(test, err)
        self.results[str(test)].update({'status': 'expected failure'})

    def addUnexpectedSuccess(self, test):
        super(DictTestResult, self).addUnexpectedSuccess(test)
        self.results[str(test)].update({'status': 'unexpected success'})

    def add_errors(self):
        self.add_error_list('error', self.errors)
        self.add_error_list('fail', self.failures)

    def add_error_list(self, flavour, errors):
        for test, err in errors:
            self.results[str(test)].update({flavour: err})

    def get_additional_results(self):
        expected_fails = unexpected_successes = skipped = 0
        try:
            results = map(len, (self.expectedFailures,
                                self.unexpectedSuccesses,
                                self.skipped))
        except AttributeError:
            pass
        else:
            expected_fails, unexpected_successes, skipped = results
        return expected_fails, skipped, unexpected_successes

    def update_global_results_info(self):
        expected_fails, skipped, unexpected_successes = self.get_additional_results()
        if not self.wasSuccessful():
            self.results['global'].update({'status': 'fail'})
            self.results['global'].update({'failures': len(self.failures)})
            self.results['global'].update({'errors': len(self.errors)})
        else:
            self.results['global'].update({'status': 'ok'})
        self.results['global'].update({'skipped': skipped})
        self.results['global'].update({'expected_fails': expected_fails})
        self.results['global'].update({'unexpected_successes': unexpected_successes})
        self.results['global'].update({'passed_count': self.get_passed_test_count(expected_fails, skipped,
                                                                                  unexpected_successes)})

    def get_passed_test_count(self, expected_fails, skipped, unexpected_successes):
        return self.testsRun - \
               (len(self.failures) + len(self.errors) + skipped + expected_fails + unexpected_successes)


class UnitTestRunner(unittest.TextTestRunner):
    resultclass = DictTestResult

    def run(self, test):
        result = super(UnitTestRunner, self)._makeResult()
        with warnings.catch_warnings():
            self._filter_warnings()
            time_taken, result = self._run_suite_with_result_formatter(result, test)
        result.add_errors()
        result.results['global'].update({'count': result.testsRun, 'time': time_taken})
        result.update_global_results_info()
        return result

    def _filter_warnings(self):
        if self.warnings:
            # if self.warnings is set, use it to filter all the warnings
            warnings.simplefilter(self.warnings)
            # if the filter is 'default' or 'always', special-case the
            # warnings from the deprecated unittest methods to show them
            # no more than once per module, because they can be fairly
            # noisy.  The -Wd and -Wa flags can be used to bypass this
            # only when self.warnings is None.
            if self.warnings in ['default', 'always']:
                warnings.filterwarnings('module',
                                        category=DeprecationWarning,
                                        message='Please use assert\w+ instead.')

    @staticmethod
    def _run_suite_with_result_formatter(result_formatter, test):
        start_time = time.time()
        startTestRun = getattr(result_formatter, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result_formatter)
        finally:
            stopTestRun = getattr(result_formatter, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stop_time = time.time()
        return stop_time - start_time, result_formatter


class DjangoHtmlTestRunner(DiscoverRunner):
    test_runner = UnitTestRunner

    def suite_result(self, suite, result, **kwargs):
        return result.results

    def setup_test_environment(self, **kwargs):
        from django.conf import settings
        setup_test_environment()
        settings.DEBUG = False

    def teardown_test_environment(self, **kwargs):
        teardown_test_environment()
