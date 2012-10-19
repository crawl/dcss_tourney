import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CSN = 'http://crawlus.somatika.net/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2012'
TEST_VERSION = USE_TEST and '0.11'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '1001')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '1101')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2012, 10, 31, 0)) # Oct 31, 00:00
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '1031')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.11', CAO + 'logfile11'),
         ('cdo-logfile-0.11', CDO + 'allgames-0.11.txt'),
         ('cszo-logfile-0.11', CSZO + 'meta/0.11/logfile'),
         ('csn-logfile-0.11', CSN + 'scoring/crawl-0.11/logfile')]
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.11', CAO + 'milestones11'),
         ('cdo-milestones-0.11', CDO + 'milestones-0.11.txt'),
         ('cszo-milestones-0.11', CSZO + 'meta/0.11/milestones'),
         ('csn-milestones-0.11', CSN + 'scoring/crawl-0.11/milestones')]
