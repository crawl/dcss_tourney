import collections
import datetime

CAO = 'http://crawl.akrasiac.org/'
CBR2 = 'https://cbro.berotato.org/'
CDI = 'https://crawl.dcss.io/crawl/'
CDO = 'http://crawl.develz.org/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu/crawl/'
CNC = 'https://archive.nemelex.cards/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2024'
TEST_VERSION = USE_TEST and '0.32'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '08162000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '08302000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2024, 8, 23, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '08292000')

# src: str: Name of server this file comes from
# local_path: str: Path this file is stored at
# url: Optional[str]: If set, 'wget -c' the file from this URL
LogSpec = collections.namedtuple('LogSpec', ('src', 'local_path', 'url'))

TEST_LOGS = USE_TEST and [
#              LogSpec('cao', 'logfiles/cao-logfile-0.32', CAO + 'logfile32'),
               LogSpec('cbr2', 'logfiles/cbr2-logfile-0.32', CBR2 + 'meta/0.32/logfile'),
               LogSpec('cdi', 'logfiles/cdi-logfile-0.32', CDI + 'meta/crawl-0.32/logfile'),
#              LogSpec('cdo', 'logfiles/cdo-logfile-0.32', CDO + 'allgames-0.32.txt'),
               LogSpec('cpo', 'logfiles/cpo-logfile-0.32', CPO + 'dcss-logfiles-0.32'),
               LogSpec('cnc', 'logfiles/cnc-logfile-0.32', CNC + 'meta/crawl-0.32/logfile'),
#              LogSpec('cue', 'logfiles/cue-logfile-0.32', CUE + 'meta/0.32/logfile'),
               LogSpec('cxc', 'logfiles/cxc-logfile-0.32', CXC + 'meta/0.32/logfile'),
               LogSpec('lld', 'logfiles/lld-logfile-0.32', LLD + 'mirror/meta/0.32/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
#              LogSpec('cao', 'milestones/cao-milestones-0.32', CAO + 'milestones32'),
               LogSpec('cbr2', 'milestones/cbr2-milestones-0.32', CBR2 + 'meta/0.32/milestones'),
               LogSpec('cdi', 'milestones/cdi-logfile-0.32', CDI + 'meta/crawl-0.32/milestones'),
#              LogSpec('cdo', 'milestones/cdo-milestones-0.32', CDO + 'milestones-0.32.txt'),
               LogSpec('cpo', 'milestones/cpo-milestones-0.32', CPO + 'dcss-milestones-0.32'),
               LogSpec('cnc', 'milestones/cnc-milestones-0.32', CNC + 'meta/crawl-0.32/milestones'),
#              LogSpec('cue', 'milestones/cue-milestones-0.32', CUE + 'meta/0.32/milestones'),
               LogSpec('cxc', 'milestones/cxc-milestones-0.32', CXC + 'meta/0.32/milestones'),
               LogSpec('lld', 'milestones/lld-milestones-0.32', LLD + 'mirror/meta/0.32/milestones'),
  ]
