import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CUE = 'http://underhound.eu:81/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CPO = 'https://crawl.project357.org/'
CWZ = 'http://webzook.net:82/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'
CJR = 'http://www.jorgrun.rocks/'

USE_TEST = True

TEST_YEAR = USE_TEST and '2016'
TEST_VERSION = USE_TEST and '0.19'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0101')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0510')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2016, 12, 1, 0))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0327')
TEST_LOGS = USE_TEST and [
         #('cao-logfile-0.19', CAO + 'logfile19'),
         #('cdo-logfile-0.19', CDO + 'allgames-0.19.txt'),
         #('cue-logfile-0.19', CUE + 'meta/0.19/logfile'),
         #('cbro-logfile-0.19', CBRO + 'meta/0.19/logfile'),
         ('cpo-logfile-0.19', CPO + 'dcss-logfiles-0.19'),
         #('cwz-logfile-0.19', CWZ + '0.19/logfile'),
         #('cxc-logfile-0.19', CXC + 'meta/0.19/logfile'),
         #('lld-logfile-0.19', LLD + 'mirror/meta/0.19/logfile'),
         #('cjr-logfile-0.19', CJR + 'meta/0.19/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
         #('cao-milestones-0.19', CAO + 'milestones18'),
         #('cdo-milestones-0.19', CDO + 'milestones-0.19.txt'),
         #('cue-milestones-0.19', CUE + 'meta/0.19/milestones'),
         #('cbro-milestones-0.19', CBRO + 'meta/0.19/milestones'),
         ('cpo-milestones-0.19', CPO + 'dcss-milestones-0.19'),
         #('cwz-milestones-0.19', CWZ + '0.19/milestones'),
         #('cxc-milestones-0.19', CXC + 'meta/0.19/milestones'),
         #('lld-milestones-0.19', LLD + 'mirror/meta/0.19/milestones'),
         #('cjr-milestones-0.19', CJR + 'meta/0.19/milestones'),
  ]

