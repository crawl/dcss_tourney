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

TEST_YEAR = USE_TEST and '2018'
TEST_VERSION = USE_TEST and '0.22'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0803')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0809')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2018, 8, 8, 23))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0808')
TEST_LOGS = USE_TEST and [
           ('cao-logfile-0.22', CAO + 'logfile22'),
           ('cbro-logfile-0.22', CBRO + 'meta/0.22/logfile'),
#          ('cdo-logfile-0.22', CDO + 'allgames-0.22.txt'),
           ('cko-logfile-0.23', CKO + 'meta/0.23/logfile'),
           ('cpo-logfile-0.22', CPO + 'dcss-logfiles-0.22'),
           ('cue-logfile-0.22', CUE + 'meta/0.22/logfile'),
           ('cwz-logfile-0.22', CWZ + '0.22/logfile'),
           ('cxc-logfile-0.22', CXC + 'meta/0.22/logfile'),
           ('lld-logfile-0.22', LLD + 'mirror/meta/0.22/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
           ('cao-milestones-0.22', CAO + 'milestones22'),
           ('cbro-milestones-0.22', CBRO + 'meta/0.22/milestones'),
#          ('cdo-milestones-0.22', CDO + 'milestones-0.22.txt'),
           ('cko-milestones-0.23', CKO + 'meta/0.23/milestones'),
           ('cpo-milestones-0.22', CPO + 'dcss-milestones-0.22'),
           ('cue-milestones-0.22', CUE + 'meta/0.22/milestones'),
           ('cwz-milestones-0.22', CWZ + '0.22/milestones'),
           ('cxc-milestones-0.22', CXC + 'meta/0.22/milestones'),
           ('lld-milestones-0.22', LLD + 'mirror/meta/0.22/milestones'),
  ]
