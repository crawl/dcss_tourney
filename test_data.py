import datetime

CAO = 'http://crawl.akrasiac.org/'
CBRO = 'http://crawl.berotato.org/crawl/'
CDO = 'http://crawl.develz.org/'
CKO = 'https://crawl.kelbi.org/crawl/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu/crawl/'
CWZ = 'https://webzook.net/soup/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2019'
TEST_VERSION = USE_TEST and '0.23'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '01292000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '02062000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2019, 2, 2, 23))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '02052000')
TEST_LOGS = USE_TEST and [
#          ('cao-logfile-0.23', CAO + 'logfile23'),
#          ('cbro-logfile-0.23', CBRO + 'meta/0.23/logfile'),
#          ('cdo-logfile-0.23', CDO + 'allgames-0.23.txt'),
           ('cko-logfile-0.23', CKO + 'meta/0.23/logfile'),
           ('cpo-logfile-0.23', CPO + 'dcss-logfiles-0.23'),
           ('cue-logfile-0.23', CUE + 'meta/0.23/logfile'),
#          ('cwz-logfile-0.23', CWZ + '0.23/logfile'),
           ('cxc-logfile-0.23', CXC + 'meta/0.23/logfile'),
           ('lld-logfile-0.23', LLD + 'mirror/meta/0.23/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
#          ('cao-milestones-0.23', CAO + 'milestones23'),
#          ('cbro-milestones-0.23', CBRO + 'meta/0.23/milestones'),
#          ('cdo-milestones-0.23', CDO + 'milestones-0.23.txt'),
           ('cko-milestones-0.23', CKO + 'meta/0.23/milestones'),
           ('cpo-milestones-0.23', CPO + 'dcss-milestones-0.23'),
           ('cue-milestones-0.23', CUE + 'meta/0.23/milestones'),
#          ('cwz-milestones-0.23', CWZ + '0.23/milestones'),
           ('cxc-milestones-0.23', CXC + 'meta/0.23/milestones'),
           ('lld-milestones-0.23', LLD + 'mirror/meta/0.23/milestones'),
  ]
