import sys
from new import instancemethod
from nose.result import TextTestResult
from nose.core import TextTestRunner
from nose.plugins.base import Plugin


class SauceTestResult(TextTestResult):

    def __init__(self, stream, descriptions, verbosity, config, sauce_stream):
        super(SauceTestResult, self).__init__(stream, descriptions, verbosity, config)
        self.sauce_stream = sauce_stream

    def log(self, test, outcome):
        #if not hasattr(test, "test") or not hasattr(test.test, "sessionId"):
        #    return
        description = self.getDescription(test)
        sessionId = test.test.sessionId
        self.sauce_stream.write("|".join((description, sessionId, outcome))+"\n")
        self.sauce_stream.flush()

    def addSuccess(self, test):
        super(SauceTestResult, self).addSuccess(test)
        self.log(test, "SUCCESS")

    def addError(self, test, err):
        super(SauceTestResult, self).addError(test, err)
        self.log(test, "ERROR")

    def addFailure(self, test, err):
        super(SauceTestResult, self).addFailure(test, err)
        self.log(test, "FAILURE")

    def addSkip(self, test, reason):
        super(SauceTestResult, self).addSkip(test, reason)
        self.log(test, "SKIP")


class SauceTestRunner(TextTestRunner):

    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1, config=None):
        super(SauceTestRunner, self).__init__(stream, descriptions, verbosity, config)

    def _makeResult(self):
        return SauceTestResult(self.stream, self.descriptions,
            self.verbosity, self.config, self.sauce_stream)

    def run(self, test):
        self.sauce_stream = open("sauce.log", "w")
        result = super(SauceTestRunner, self).run(test)
        self.sauce_stream.close()
        self.sauce_stream = None
        return result


def run_foo(self, result = None):
    if result is None: result = self.defaultTestResult()
    result.startTest(self)
    testMethod = getattr(self, self._testMethodName)
    try:
        try:
            self.setUp()
        except KeyboardInterrupt:
            raise
        except:
            result.addError(self, sys.exc_info())
            return

        ok = False
        try:
            testMethod()
            ok = True
        except self.failureException:
            result.addFailure(self, sys.exc_info())
        except KeyboardInterrupt:
            raise
        except:
            result.addError(self, sys.exc_info())

        try:
            self.tearDown()
        except KeyboardInterrupt:
            raise
        except:
            result.addError(self, sys.exc_info())
            ok = False
        if ok: result.addSuccess(self)
    finally:
        result.stopTest(self)



class Sauce(Plugin):

    def prepareTestRunner(self, runner):
        return SauceTestRunner(runner.stream, runner.descriptions, runner.verbosity, runner.config)
        
    def prepareTestCase(self, test):
                
        test.test.run = instancemethod(run_foo, test.test)
        
        return test.test

        

