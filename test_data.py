import collections
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
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '11012000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2019, 10, 26, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '01012000')

# src: str: Name of server this file comes from
# local_path: str: Path this file is stored at
# url: Optional[str]: If set, 'wget -c' the file from this URL
LogSpec = collections.namedtuple('LogSpec', ('src', 'local_path', 'url'))

TEST_LOGS = USE_TEST and [
#           LogSpec('cao', 'logfiles/cao-logfile-0.24', None),  # CAO + 'logfile24'),
#           LogSpec('cbro', 'logfiles/cbro-logfile-0.24', None),  # CBRO + 'meta/0.24/logfile'),
#           LogSpec('cdo', 'logfiles/cdo-logfile-0.24', None),  # CDO + 'allgames-0.24.txt'),
#           LogSpec('cko', 'logfiles/cko-logfile-0.24', None),  # CKO + 'meta/0.24/logfile'),
           LogSpec('cpo', 'logfiles/cpo-logfile-0.24', None),  # CPO + 'dcss-logfiles-0.24'),
#           LogSpec('cue', 'logfiles/cue-logfile-0.24', None),  # CUE + 'meta/0.24/logfile'),
#           LogSpec('cwz', 'logfiles/cwz-logfile-0.24', None),  # CWZ + '0.24/logfile'),
#           LogSpec('cxc', 'logfiles/cxc-logfile-0.24', None),  # CXC + 'meta/0.24/logfile'),
#           LogSpec('lld', 'logfiles/lld-logfile-0.24', None),  # LLD + 'mirror/meta/0.24/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
#           LogSpec('cao', 'milestones/cao-milestones-0.24', None),  # CAO + 'milestones24'),
#           LogSpec('cbro', 'milestones/cbro-milestones-0.24', None),  # CBRO + 'meta/0.24/milestones'),
#           LogSpec('cdo', 'milestones/cdo-milestones-0.24', None),  # CDO + 'milestones-0.24.txt'),
#           LogSpec('cko', 'milestones/cko-milestones-0.24', None),  # CKO + 'meta/0.24/milestones'),
           LogSpec('cpo', 'milestones/cpo-milestones-0.24', None),  # CPO + 'dcss-milestones-0.24'),
#           LogSpec('cue', 'milestones/cue-milestones-0.24', None),  # CUE + 'meta/0.24/milestones'),
#           LogSpec('cwz', 'milestones/cwz-milestones-0.24', None),  # CWZ + '0.24/milestones'),
#           LogSpec('cxc', 'milestones/cxc-milestones-0.24', None),  # CXC + 'meta/0.24/milestones'),
#           LogSpec('lld', 'milestones/lld-milestones-0.24', None),  # LLD + 'mirror/meta/0.24/milestones'),
  ]
