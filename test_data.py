import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CUE = 'http://underhound.eu:81/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CPO = 'http://crawl.project357.org/'
CWZ = 'http://webzook.net:82/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2015'
TEST_VERSION = USE_TEST and '0.18'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '1101')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '1201')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2015, 12, 1, 0))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '1101')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.18', CAO + 'logfile17'),
         #('cdo-logfile-0.18', CDO + 'allgames-0.18.txt'),
         #('cue-logfile-0.18', CUE + 'meta/0.18/logfile'),
         ('cbro-logfile-0.18', CBRO + 'meta/0.18/logfile'),
         ('cpo-logfile-0.18', CPO + 'dcss-logfiles-0.18'),
         #('cwz-logfile-0.18', CWZ + '0.18/logfile'),
         #('cxc-logfile-0.18', CXC + 'meta/0.18/logfile'),
         ('lld-logfile-0.18', LLD + 'mirror/meta/0.18/logfile')]

TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.18', CAO + 'milestones17'),
         #('cdo-milestones-0.18', CDO + 'milestones-0.18.txt'),
         #('cue-milestones-0.18', CUE + 'meta/0.18/milestones'),
         ('cbro-milestones-0.18', CBRO + 'meta/0.18/milestones'),
         ('cpo-milestones-0.18', CPO + 'dcss-milestones-0.18'),
         #('cwz-milestones-0.18', CWZ + '0.18/milestones'),
         #('cxc-milestones-0.18', CXC + 'meta/0.18/milestones'),
         ('lld-milestones-0.18', LLD + 'mirror/meta/0.18/milestones')]

