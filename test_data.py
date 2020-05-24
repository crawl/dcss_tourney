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
TEST_START_TIME = USE_TEST and (TEST_YEAR + '10252000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '11102000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2019, 10, 24, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '01012000')
TEST_LOGS = USE_TEST and [
          #  ('logfiles/cao-logfile-0.24', CAO + 'logfile24'),
#           ('logfiles/cbro-logfile-0.24', CBRO + 'meta/0.24/logfile'),
#           ('logfiles/cdo-logfile-0.24', CDO + 'allgames-0.24.txt'),
#           ('logfiles/cko-logfile-0.24', CKO + 'meta/0.24/logfile'),
           ('logfiles/cpo-logfile-0.24', CPO + 'dcss-logfiles-0.24'),
#           ('logfiles/cue-logfile-0.24', CUE + 'meta/0.24/logfile'),
#           ('logfiles/cwz-logfile-0.24', CWZ + '0.24/logfile'),
          #  ('logfiles/cxc-logfile-0.24', CXC + 'meta/0.24/logfile'),
          #  ('logfiles/lld-logfile-0.24', LLD + 'mirror/meta/0.24/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
          #  ('milestones/cao-milestones-0.24', CAO + 'milestones24'),
#           ('milestones/cbro-milestones-0.24', CBRO + 'meta/0.24/milestones'),
#           ('milestones/cdo-milestones-0.24', CDO + 'milestones-0.24.txt'),
#           ('milestones/cko-milestones-0.24', CKO + 'meta/0.24/milestones'),
           ('milestones/cpo-milestones-0.24', CPO + 'dcss-milestones-0.24'),
#           ('milestones/cue-milestones-0.24', CUE + 'meta/0.24/milestones'),
#           ('milestones/cwz-milestones-0.24', CWZ + '0.24/milestones'),
          #  ('milestones/cxc-milestones-0.24', CXC + 'meta/0.24/milestones'),
          #  ('milestones/lld-milestones-0.24', LLD + 'mirror/meta/0.24/milestones'),
  ]
