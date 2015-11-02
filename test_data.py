import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CUE = 'http://underhound.eu:81/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CPO = 'http://crawl.project357.org/'
CWZ = 'http://webzook.net:82/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2015'
TEST_VERSION = USE_TEST and '0.17'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '1101')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '1201')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2015, 11, 1, 0))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '1101')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.17', CAO + 'logfile17'),
         ('cdo-logfile-0.17', CDO + 'allgames-0.17.txt'),
         ('cue-logfile-0.17', CUE + 'meta/0.17/logfile'),
         ('cbro-logfile-0.17', CBRO + 'meta/0.17/logfile'),
         ('cpo-logfile-0.17', CPO + 'dcss-logfiles-0.17'),
         ('cwz-logfile-0.17', CWZ + '0.17/logfile'),
         ('cxc-logfile-0.17', CXC + 'meta/0.17/logfile'),
         ('lld-logfile-0.17', LLD + 'mirror/meta/0.17/logfile'),
         ('cszo-logfile-0.17', CSZO + 'meta/0.17/logfile')]
# this line should be used on CSZO instead:
#         'cszo-logfile-0.17']
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.17', CAO + 'milestones17'),
         ('cdo-milestones-0.17', CDO + 'milestones-0.17.txt'),
         ('cue-milestones-0.17', CUE + 'meta/0.17/milestones'),
         ('cbro-milestones-0.17', CBRO + 'meta/0.17/milestones'),
         ('cpo-milestones-0.17', CPO + 'dcss-milestones-0.17'),
         ('cwz-milestones-0.17', CWZ + '0.17/milestones'),
         ('cxc-milestones-0.17', CXC + 'meta/0.17/milestones'),
         ('lld-milestones-0.17', LLD + 'mirror/meta/0.17/milestones'),
         ('cszo-milestones-0.17', CSZO + 'meta/0.17/milestones')]
# this line should be used on CSZO instead:
#         'cszo-milestones-0.17']
