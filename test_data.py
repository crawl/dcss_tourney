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
TEST_VERSION = USE_TEST and '0.24'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '10222000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '10252000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2019, 10, 24, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '10242000')
TEST_LOGS = USE_TEST and [
           ('cao-logfile-0.24', CAO + 'logfile24'),
#           ('cbro-logfile-0.24', CBRO + 'meta/0.24/logfile'),
#           ('cdo-logfile-0.24', CDO + 'allgames-0.24.txt'),
#           ('cko-logfile-0.24', CKO + 'meta/0.24/logfile'),
           ('cpo-logfile-0.24', CPO + 'dcss-logfiles-0.24'),
#           ('cue-logfile-0.24', CUE + 'meta/0.24/logfile'),
#           ('cwz-logfile-0.24', CWZ + '0.24/logfile'),
           ('cxc-logfile-0.24', CXC + 'meta/0.24/logfile'),
           ('lld-logfile-0.24', LLD + 'mirror/meta/0.24/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
           ('cao-milestones-0.24', CAO + 'milestones24'),
#           ('cbro-milestones-0.24', CBRO + 'meta/0.24/milestones'),
#           ('cdo-milestones-0.24', CDO + 'milestones-0.24.txt'),
#           ('cko-milestones-0.24', CKO + 'meta/0.24/milestones'),
           ('cpo-milestones-0.24', CPO + 'dcss-milestones-0.24'),
#           ('cue-milestones-0.24', CUE + 'meta/0.24/milestones'),
#           ('cwz-milestones-0.24', CWZ + '0.24/milestones'),
           ('cxc-milestones-0.24', CXC + 'meta/0.24/milestones'),
           ('lld-milestones-0.24', LLD + 'mirror/meta/0.24/milestones'),
  ]
