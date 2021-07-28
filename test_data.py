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

USE_TEST = True

TEST_YEAR = USE_TEST and '2021'
TEST_VERSION = USE_TEST and '0.27'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '07242000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '07292000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2021, 7, 28, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '07282000')

# src: str: Name of server this file comes from
# local_path: str: Path this file is stored at
# url: Optional[str]: If set, 'wget -c' the file from this URL
LogSpec = collections.namedtuple('LogSpec', ('src', 'local_path', 'url'))

TEST_LOGS = USE_TEST and [
             LogSpec('cao', 'logfiles/cao-logfile-0.27', CAO + 'logfile27'),
             LogSpec('cbr2', 'logfiles/cbr2-logfile-0.27', CBR2 + 'meta/0.27/logfile'),
#            LogSpec('cdo', 'logfiles/cdo-logfile-0.27', CDO + 'allgames-0.27.txt'),
             LogSpec('cko', 'logfiles/cko-logfile-0.27', CKO + 'meta/0.27/logfile'),
             LogSpec('cpo', 'logfiles/cpo-logfile-0.27', CPO + 'dcss-logfiles-0.27'),
#            LogSpec('cue', 'logfiles/cue-logfile-0.27', CUE + 'meta/0.27/logfile'),
#            LogSpec('cwz', 'logfiles/cwz-logfile-0.27', CWZ + '0.27/logfile'),
             LogSpec('cxc', 'logfiles/cxc-logfile-0.27', CXC + 'meta/0.27/logfile'),
             LogSpec('lld', 'logfiles/lld-logfile-0.27', LLD + 'mirror/meta/0.27/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
             LogSpec('cao', 'milestones/cao-milestones-0.27', CAO + 'milestones27'),
             LogSpec('cbr2', 'milestones/cbr2-milestones-0.27', CBR2 + 'meta/0.27/milestones'),
#            LogSpec('cdo', 'milestones/cdo-milestones-0.27', CDO + 'milestones-0.27.txt'),
             LogSpec('cko', 'milestones/cko-milestones-0.27', CKO + 'meta/0.27/milestones'),
             LogSpec('cpo', 'milestones/cpo-milestones-0.27', CPO + 'dcss-milestones-0.27'),
#            LogSpec('cue', 'milestones/cue-milestones-0.27', CUE + 'meta/0.27/milestones'),
#            LogSpec('cwz', 'milestones/cwz-milestones-0.27', CWZ + '0.27/milestones'),
             LogSpec('cxc', 'milestones/cxc-milestones-0.27', CXC + 'meta/0.27/milestones'),
             LogSpec('lld', 'milestones/lld-milestones-0.27', LLD + 'mirror/meta/0.27/milestones'),
  ]
