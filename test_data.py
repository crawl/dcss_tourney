import datetime

CAO = 'http://crawl.akrasiac.org/'
CBRO = 'http://crawl.berotato.org/crawl/'
CDO = 'http://crawl.develz.org/'
CJR = 'https://crawl.jorgrun.rocks/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu:81/crawl/'
CWZ = 'https://webzook.net/soup/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = True

TEST_YEAR = USE_TEST and '2017'
TEST_VERSION = USE_TEST and '0.20'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0519')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0604')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2017, 5, 26, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0603')
TEST_LOGS = USE_TEST and [
          ('cao-logfile-0.20', CAO + 'logfile20'),
          ('cbro-logfile-0.20', CBRO + 'meta/0.20/logfile'),
#         ('cdo-logfile-0.20', CDO + 'allgames-0.20.txt'),
          ('cjr-logfile-0.20', CJR + 'meta/0.20/logfile'),
          ('cpo-logfile-0.20', CPO + 'dcss-logfiles-0.20'),
          ('cue-logfile-0.20', CUE + 'meta/0.20/logfile'),
          ('cwz-logfile-0.20', CWZ + '0.20/logfile'),
          ('cxc-logfile-0.20', CXC + 'meta/0.20/logfile'),
          ('lld-logfile-0.20', LLD + 'mirror/meta/0.20/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
          ('cao-milestones-0.20', CAO + 'milestones20'),
          ('cbro-milestones-0.20', CBRO + 'meta/0.20/milestones'),
#         ('cdo-milestones-0.20', CDO + 'milestones-0.20.txt'),
          ('cjr-milestones-0.20', CJR + 'meta/0.20/milestones'),
          ('cpo-milestones-0.20', CPO + 'dcss-milestones-0.20'),
          ('cue-milestones-0.20', CUE + 'meta/0.20/milestones'),
          ('cwz-milestones-0.20', CWZ + '0.20/milestones'),
          ('cxc-milestones-0.20', CXC + 'meta/0.20/milestones'),
          ('lld-milestones-0.20', LLD + 'mirror/meta/0.20/milestones'),
  ]
