import collections
import datetime

CAO = 'https://crawl.akrasiac.org/'
CBR2 = 'https://cbro.berotato.org/'
CDI = 'https://crawl.dcss.io/crawl/'
CDO = 'https://crawl.develz.org/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu/crawl/'
CNC = 'https://archive.nemelex.cards/'
CXC = 'https://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2025'
TEST_VERSION = USE_TEST and '0.33'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '04262000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '05022000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2025, 5, 2, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '05012000')

# src: str: Name of server this file comes from
# local_path: str: Path this file is stored at
# url: Optional[str]: If set, 'wget -c' the file from this URL
LogSpec = collections.namedtuple('LogSpec', ('src', 'local_path', 'url'))

TEST_LOGS = USE_TEST and [
                LogSpec('cao', 'logfiles/cao-logfile-0.33', CAO + 'logfile33'),
                LogSpec('cbr2', 'logfiles/cbr2-logfile-0.33', CBR2 + 'meta/0.33/logfile'),
                LogSpec('cdi', 'logfiles/cdi-logfile-0.33', CDI + 'meta/crawl-0.33/logfile'),
#               LogSpec('cdo', 'logfiles/cdo-logfile-0.33', CDO + 'allgames-0.33.txt'),
                LogSpec('cpo', 'logfiles/cpo-logfile-0.33', CPO + 'dcss-logfiles-0.33'),
                LogSpec('cnc', 'logfiles/cnc-logfile-0.33', CNC + 'meta/crawl-0.33/logfile'),
                LogSpec('cue', 'logfiles/cue-logfile-0.33', CUE + 'meta/0.33/logfile'),
                LogSpec('cxc', 'logfiles/cxc-logfile-0.33', CXC + 'meta/0.33/logfile'),
                LogSpec('lld', 'logfiles/lld-logfile-0.33', LLD + 'mirror/meta/0.33/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
                LogSpec('cao', 'milestones/cao-milestones-0.33', CAO + 'milestones33'),
                LogSpec('cbr2', 'milestones/cbr2-milestones-0.33', CBR2 + 'meta/0.33/milestones'),
                LogSpec('cdi', 'milestones/cdi-logfile-0.33', CDI + 'meta/crawl-0.33/milestones'),
#               LogSpec('cdo', 'milestones/cdo-milestones-0.33', CDO + 'milestones-0.33.txt'),
                LogSpec('cpo', 'milestones/cpo-milestones-0.33', CPO + 'dcss-milestones-0.33'),
                LogSpec('cnc', 'milestones/cnc-milestones-0.33', CNC + 'meta/crawl-0.33/milestones'),
                LogSpec('cue', 'milestones/cue-milestones-0.33', CUE + 'meta/0.33/milestones'),
                LogSpec('cxc', 'milestones/cxc-milestones-0.33', CXC + 'meta/0.33/milestones'),
                LogSpec('lld', 'milestones/lld-milestones-0.33', LLD + 'mirror/meta/0.33/milestones'),
  ]
