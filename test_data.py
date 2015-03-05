import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CLN = 'http://crawl.lantea.net/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CPO = 'http://crawl.project357.org/'
CWZ = 'http://webzook.net:82/'
CXC = 'http://crawl.xtahua.com/crawl/'
LLD = 'http://lazy-life.ddo.jp/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2015'
TEST_VERSION = USE_TEST and '0.16'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0301')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0401')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2015, 3, 1, 0))
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0301')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.16', CAO + 'logfile16'),
         ('cdo-logfile-0.16', CDO + 'allgames-0.16.txt'),
         ('cln-logfile-0.16', CLN + 'meta/0.16/logfile'),
         ('cbro-logfile-0.16', CBRO + 'meta/0.16/logfile'),
         ('cpo-logfile-0.16', CPO + 'dcss-logfiles-0.16'),
         ('cwz-logfile-0.16', CWZ + '0.16/logfile'),
         ('cxc-logfile-0.16', CXC + 'meta/0.16/logfile'),
         ('lld-logfile-0.16', LLD + 'mirror/meta/0.16/logfile'),
         ('cszo-logfile-0.16', CSZO + 'meta/0.16/logfile')]
# this line should be used on CSZO instead:
#         'cszo-logfile-0.16']
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.16', CAO + 'milestones16'),
         ('cdo-milestones-0.16', CDO + 'milestones-0.16.txt'),
         ('cln-milestones-0.16', CLN + 'meta/0.16/milestones'),
         ('cbro-milestones-0.16', CBRO + 'meta/0.16/milestones'),
         ('cpo-milestones-0.16', CPO + 'dcss-milestones-0.16'),
         ('cwz-milestones-0.16', CWZ + '0.16/milestones'),
         ('cxc-milestones-0.16', CXC + 'meta/0.16/milestones'),
         ('lld-milestones-0.16', LLD + 'mirror/meta/0.16/milestones'),
         ('cszo-milestones-0.16', CSZO + 'meta/0.16/milestones')]
# this line should be used on CSZO instead:
#         'cszo-milestones-0.16']
