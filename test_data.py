CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CSN = 'http://crawlus.somatika.net/'

USE_TEST = True

TEST_YEAR = USE_TEST and '2012'
TEST_VERSION = USE_TEST and '0.11'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0801')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '1001')
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0931')
TEST_LOGS = USE_TEST and [
         ('cdo-logfile-0.11', CDO + 'allgames-0.11.txt'),
         ('cszo-logfile-0.11', CSZO + 'meta/0.11/logfile'),
         ('csn-logfile-0.11', CSN + 'scoring/crawl-trunk/logfile')]
TEST_MILESTONES = USE_TEST and [
         ('cdo-milestones-0.11', CDO + 'milestones-0.11.txt'),
         ('cszo-milestones-0.11', CSZO + 'meta/0.11/milestones'),
         ('csn-milestones-0.11', CSN + 'scoring/crawl-trunk/milestones')]
