import collections
import datetime

CAO = 'http://crawl.akrasiac.org/'
CBR2 = 'https://cbro.berotato.org/'
CDI = 'https://crawl.dcss.io/crawl/'
CDO = 'http://crawl.develz.org/'
CKO = 'https://crawl.kelbi.org/crawl/'
CPO = 'https://crawl.project357.org/'
CUE = 'https://underhound.eu/crawl/'
CWZ = 'https://webzook.net/soup/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2023'
TEST_VERSION = USE_TEST and '0.30'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '05052000')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '05212000')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2023, 5, 12, 20))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '05202000')

# src: str: Name of server this file comes from
# local_path: str: Path this file is stored at
# url: Optional[str]: If set, 'wget -c' the file from this URL
LogSpec = collections.namedtuple('LogSpec', ('src', 'local_path', 'url'))

TEST_LOGS = USE_TEST and [
             LogSpec('cao', 'logfiles/cao-logfile-0.30', CAO + 'logfile30'),
             LogSpec('cbr2', 'logfiles/cbr2-logfile-0.30', CBR2 + 'meta/0.30/logfile'),
#            LogSpec('cdi', 'logfiles/cdi-logfile-0.30', CDI + 'meta/crawl-bot-0.30/logfile'),
#            LogSpec('cdo', 'logfiles/cdo-logfile-0.30', CDO + 'allgames-0.30.txt'),
             LogSpec('cko', 'logfiles/cko-logfile-0.30', CKO + 'meta/0.30/logfile'),
             LogSpec('cpo', 'logfiles/cpo-logfile-0.30', CPO + 'dcss-logfiles-0.30'),
             LogSpec('cue', 'logfiles/cue-logfile-0.30', CUE + 'meta/0.30/logfile'),
             LogSpec('cwz', 'logfiles/cwz-logfile-0.30', CWZ + '0.30/logfile'),
             LogSpec('cxc', 'logfiles/cxc-logfile-0.30', CXC + 'meta/0.30/logfile'),
             LogSpec('lld', 'logfiles/lld-logfile-0.30', LLD + 'mirror/meta/0.30/logfile'),
  ]

TEST_MILESTONES = USE_TEST and [
             LogSpec('cao', 'milestones/cao-milestones-0.30', CAO + 'milestones30'),
             LogSpec('cbr2', 'milestones/cbr2-milestones-0.30', CBR2 + 'meta/0.30/milestones'),
#            LogSpec('cdi', 'milestones/cdi-logfile-0.30', CDI + 'meta/crawl-bot-0.30/milestones'),
#            LogSpec('cdo', 'milestones/cdo-milestones-0.30', CDO + 'milestones-0.30.txt'),
             LogSpec('cko', 'milestones/cko-milestones-0.30', CKO + 'meta/0.30/milestones'),
             LogSpec('cpo', 'milestones/cpo-milestones-0.30', CPO + 'dcss-milestones-0.30'),
             LogSpec('cue', 'milestones/cue-milestones-0.30', CUE + 'meta/0.30/milestones'),
             LogSpec('cwz', 'milestones/cwz-milestones-0.30', CWZ + '0.30/milestones'),
             LogSpec('cxc', 'milestones/cxc-milestones-0.30', CXC + 'meta/0.30/milestones'),
             LogSpec('lld', 'milestones/lld-milestones-0.30', LLD + 'mirror/meta/0.30/milestones'),
  ]
