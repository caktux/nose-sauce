import urllib2
import StringIO

SAUCEURL = "https://saucelabs.com/rest/%(u)s/jobs/%(j)s/assets/%(r)s"
SAUCEURL_WITHAUTH = "https://%(u)s:%(p)s@saucelabs.com/rest/%(u)s/jobs/%(j)s/assets/%(r)s"
 
class LogParser(object):

    """
    Given a session ID, i parse the selenium-server.log and yield an orderered lists of
    steps, whether or not that test passed and a url to a screenshot.
    """

    def __init__(self, username, apikey, embed_creds=False):
        self.username = username
        self.apikey = apikey
        self.embed_creds = embed_creds

        self.build_urllib2_opener()

    def build_urllib2_opener(self):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, "https://saucelabs.com/", self.username, self.apikey)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        self.opener = urllib2.build_opener(handler)

    def parse_log(self, session):
        logurl = self.get_url(session, "selenium-server.log", embed_creds=False)

        log = self.opener.open(logurl).read()
        results = []

        fp = StringIO.StringIO(log)

        line = fp.readline()[20:]
        while line:
            line, command, result, retval = self.parse_command(line, fp)

            line, shot = self.get_command(line, fp)

            # Might have one of these, might not:
            #17:08:04.280 INFO - Command request: captureScreenshot[shot_35.png, ] on session f53271cfce714e0080612387ada6fa7e

            screenshot = None
            if shot.startswith("captureScreenshot"):
                endpoint = shot.find(".png, ] on session ") - 6
                startpoint = shot.find("shot_") + 5
                screenshot_num = shot[startpoint:endpoint].rjust(4, "0")
                screenshot = self.get_url(session, "%sscreenshot.png" % screenshot_num)

                line, result, retval = self.get_result(line, fp)

            results.append(dict(command=command, result=result, retval=retval, screenshot=screenshot))

        screenshots = [x['screenshot'] for x in results if x['screenshot']]
        last_screenshot = ""
        if screenshots:
            last_screenshot = screenshots[-1]

        video_flv = self.get_url(session, "video.flv")
        selenium_log = self.get_url(session, "selenium-server.log")

        return dict(session=session, results=results, last_screenshot=last_screenshot,
            video_flv=video_flv, selenium_log=selenium_log)

    def get_command(self, line, fp):
        while line and not line.startswith("Command request"):
            line = fp.readline()[20:]

        # Have a line that looks something like this:
        #17:08:04.248 INFO - Command request: click[//dl[@id='plone-contentmenu-workflow']/dt/a/span[3], ] on session f53271cfce714e0080612387ada6fa7e

        if line.startswith("Command request"):
            return line, line[17:line.find(" on session ")]

        return line, ""

    def get_result(self, line, fp):
        while line and not line.startswith("Got result"):
            line = fp.readline()[20:]

        # Have a line that looks something like this:
        #17:08:04.670 INFO - Got result: OK on session f53271cfce714e0080612387ada6fa7e

        result = line[12:line.find(" on session ")].strip()
        retval = None

        if result.startswith("OK,"):
            retval = result[3:]
            result = "OK"

        return line, result, retval

    def parse_command(self, line, fp):
        line, command = self.get_command(line, fp)
        line, result, retval = self.get_result(line, fp)

        return line, command, result, retval

    def get_url(self, session, resource, embed_creds=None):
        if embed_creds is None:
            embed_creds = self.embed_creds

        if embed_creds:
            return SAUCEURL_WITHAUTH % {
                "u": self.username,
                "p": self.apikey,
                "j": session,
                "r": resource,
                }
        else:
            return SAUCEURL % {
                "u": self.username,
                "j": session,
                "r": resource,
                }

if __name__ == "__main__":
    l = LogParser("username", "apikey", embed_creds=True)
    print l.parse_log('sessionid')

