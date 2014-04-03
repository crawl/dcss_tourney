import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CLN = 'http://crawl.lantea.net/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CKR = 'http://kr.dobrazupa.org/'
RHF = 'http://rl.heh.fi/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2014'
TEST_VERSION = USE_TEST and '0.14'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0401')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0408')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2012, 5, 1, 0)) # May 1, 00:00
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0407')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.14', CAO + 'logfile14'),
#         ('cdo-logfile-0.14', CDO + 'allgames-0.14.txt'),
         ('cln-logfile-0.14', CLN + 'meta/0.14/logfile'),
#         ('rhf-logfile-0.14', RHF + 'meta/crawl-0.14/logfile'),
         ('cbro-logfile-0.14', CBRO + 'meta/0.14/logfile'),
         ('ckr-logfile-0.14', CKR + 'www/0.14/logfile'),
         ('cszo-logfile-0.14', CSZO + 'meta/0.14/logfile')]
# this line should be used on CSZO instead:
#         'cszo-logfile-0.14']
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.14', CAO + 'milestones14'),
#         ('cdo-milestones-0.14', CDO + 'milestones-0.14.txt'),
         ('cln-milestones-0.14', CLN + 'meta/0.14/milestones'),
#         ('rhf-milestones-0.14', RHF + 'meta/crawl-0.14/milestones'),
         ('cbro-milestones-0.14', CBRO + 'meta/0.14/milestones'),
         ('ckr-milestones-0.14', CKR + 'www/0.14/milestones'),
         ('cszo-milestones-0.14', CSZO + 'meta/0.14/milestones')]
# this line should be used on CSZO instead:
#         'cszo-milestones-0.14']
