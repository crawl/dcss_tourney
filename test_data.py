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

TEST_YEAR = USE_TEST and '2018'
TEST_VERSION = USE_TEST and '0.21'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0101')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0104')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2018, 1, 12, 23))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0120')
TEST_LOGS = USE_TEST and [
          ('cao-logfile-0.21', CAO + 'logfile21'),
          ('cbro-logfile-0.21', CBRO + 'meta/0.21/logfile'),
#         ('cdo-logfile-0.21', CDO + 'allgames-0.21.txt'),
          ('cjr-logfile-0.21', CJR + 'meta/0.21/logfile'),
          ('cpo-logfile-0.21', CPO + 'dcss-logfiles-0.21'),
          ('cue-logfile-0.21', CUE + 'meta/0.21/logfile'),
          ('cwz-logfile-0.21', CWZ + '0.21/logfile'),
          ('cxc-logfile-0.21', CXC + 'meta/0.21/logfile'),
          ('lld-logfile-0.21', LLD + 'mirror/meta/0.21/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
          ('cao-milestones-0.21', CAO + 'milestones21'),
          ('cbro-milestones-0.21', CBRO + 'meta/0.21/milestones'),
#         ('cdo-milestones-0.21', CDO + 'milestones-0.21.txt'),
          ('cjr-milestones-0.21', CJR + 'meta/0.21/milestones'),
          ('cpo-milestones-0.21', CPO + 'dcss-milestones-0.21'),
          ('cue-milestones-0.21', CUE + 'meta/0.21/milestones'),
          ('cwz-milestones-0.21', CWZ + '0.21/milestones'),
          ('cxc-milestones-0.21', CXC + 'meta/0.21/milestones'),
          ('lld-milestones-0.21', LLD + 'mirror/meta/0.21/milestones'),
  ]
