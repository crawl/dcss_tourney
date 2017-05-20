import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CUE = 'https://underhound.eu:81/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CPO = 'https://crawl.project357.org/'
CWZ = 'http://webzook.net:82/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'
CJR = 'https://www.jorgrun.rocks/'

USE_TEST = True

TEST_YEAR = USE_TEST and '2017'
TEST_VERSION = USE_TEST and '0.20'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0519')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0604')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2017, 5, 26, 2000))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0603')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.20', CAO + 'logfile20'),
         ('cdo-logfile-0.20', CDO + 'allgames-0.20.txt'),
         ('cue-logfile-0.20', CUE + 'meta/0.20/logfile'),
         ('cbro-logfile-0.20', CBRO + 'meta/0.20/logfile'),
         ('cpo-logfile-0.20', CPO + 'dcss-logfiles-0.20'),
         ('cwz-logfile-0.20', CWZ + '0.20/logfile'),
         ('cxc-logfile-0.20', CXC + 'meta/0.20/logfile'),
         ('lld-logfile-0.20', LLD + 'mirror/meta/0.20/logfile'),
         ('cjr-logfile-0.20', CJR + 'meta/0.20/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.20', CAO + 'milestones20'),
         ('cdo-milestones-0.20', CDO + 'milestones-0.20.txt'),
         ('cue-milestones-0.20', CUE + 'meta/0.20/milestones'),
         ('cbro-milestones-0.20', CBRO + 'meta/0.20/milestones'),
         ('cpo-milestones-0.20', CPO + 'dcss-milestones-0.20'),
         ('cwz-milestones-0.20', CWZ + '0.20/milestones'),
         ('cxc-milestones-0.20', CXC + 'meta/0.20/milestones'),
         ('lld-milestones-0.20', LLD + 'mirror/meta/0.20/milestones'),
         ('cjr-milestones-0.20', CJR + 'meta/0.20/milestones'),
  ]

