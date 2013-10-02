import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CLN = 'http://crawl.lantea.net/crawl/'
RHF = 'http://rl.heh.fi/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2013'
TEST_VERSION = USE_TEST and '0.13'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '1001')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '1008')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2012, 11, 1, 0)) # Nov 1, 00:00
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '1007')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.13', CAO + 'logfile13'),
#         ('cdo-logfile-0.13', CDO + 'allgames-0.13.txt'),
         ('cln-logfile-0.13', CLN + 'meta/0.13/logfile'),
#         ('rhf-logfile-0.13', RHF + 'meta/crawl-0.13/logfile'),
         ('cszo-logfile-0.13', CSZO + 'meta/0.13/logfile')]
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.13', CAO + 'milestones13'),
#         ('cdo-milestones-0.13', CDO + 'milestones-0.13.txt'),
         ('cln-milestones-0.13', CLN + 'meta/0.13/milestones'),
#         ('rhf-milestones-0.13', RHF + 'meta/crawl-0.13/milestones'),
         ('cszo-milestones-0.13', CSZO + 'meta/0.13/milestones')]
