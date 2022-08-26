import collections
import datetime

CAO = 'http://crawl.akrasiac.org/'
CBR2 = 'https://cbro.berotato.org/'
CDO = 'http://crawl.develz.org/'
CKO = 'https://crawl.kelbi.org/crawl/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu/crawl/'
CWZ = 'https://webzook.net/soup/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2022'
TEST_VERSION = USE_TEST and '0.29'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '08232000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '08252000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2022, 8, 24, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '08242000')

# src: str: Name of server this file comes from
# local_path: str: Path this file is stored at
# url: Optional[str]: If set, 'wget -c' the file from this URL
LogSpec = collections.namedtuple('LogSpec', ('src', 'local_path', 'url'))

TEST_LOGS = USE_TEST and [
             LogSpec('cao', 'logfiles/cao-logfile-0.29', CAO + 'logfile29'),
             LogSpec('cbr2', 'logfiles/cbr2-logfile-0.29', CBR2 + 'meta/0.29/logfile'),
#            LogSpec('cdo', 'logfiles/cdo-logfile-0.29', CDO + 'allgames-0.29.txt'),
             LogSpec('cko', 'logfiles/cko-logfile-0.29', CKO + 'meta/0.29/logfile'),
             LogSpec('cpo', 'logfiles/cpo-logfile-0.29', CPO + 'dcss-logfiles-0.29'),
             LogSpec('cue', 'logfiles/cue-logfile-0.29', CUE + 'meta/0.29/logfile'),
             LogSpec('cwz', 'logfiles/cwz-logfile-0.29', CWZ + '0.29/logfile'),
             LogSpec('cxc', 'logfiles/cxc-logfile-0.29', CXC + 'meta/0.29/logfile'),
             LogSpec('lld', 'logfiles/lld-logfile-0.29', LLD + 'mirror/meta/0.29/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
             LogSpec('cao', 'milestones/cao-milestones-0.29', CAO + 'milestones29'),
             LogSpec('cbr2', 'milestones/cbr2-milestones-0.29', CBR2 + 'meta/0.29/milestones'),
#            LogSpec('cdo', 'milestones/cdo-milestones-0.29', CDO + 'milestones-0.29.txt'),
             LogSpec('cko', 'milestones/cko-milestones-0.29', CKO + 'meta/0.29/milestones'),
             LogSpec('cpo', 'milestones/cpo-milestones-0.29', CPO + 'dcss-milestones-0.29'),
             LogSpec('cue', 'milestones/cue-milestones-0.29', CUE + 'meta/0.29/milestones'),
             LogSpec('cwz', 'milestones/cwz-milestones-0.29', CWZ + '0.29/milestones'),
             LogSpec('cxc', 'milestones/cxc-milestones-0.29', CXC + 'meta/0.29/milestones'),
             LogSpec('lld', 'milestones/lld-milestones-0.29', LLD + 'mirror/meta/0.29/milestones'),
  ]
