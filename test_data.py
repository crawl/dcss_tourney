import datetime

CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'
CSZO = 'http://dobrazupa.org/'
CLN = 'http://crawl.lantea.net/crawl/'
CBRO = 'http://crawl.berotato.org/crawl/'
CKR = 'http://kr.dobrazupa.org/'
RHF = 'http://rl.heh.fi/'

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
#         ('cdo-logfile-0.16', CDO + 'allgames-0.16.txt'),
         ('cln-logfile-0.16', CLN + 'meta/0.16/logfile'),
#         ('rhf-logfile-0.14', RHF + 'meta/crawl-0.14/logfile'),
         ('cbro-logfile-0.16', CBRO + 'meta/0.16/logfile'),
#         ('ckr-logfile-0.15', CKR + 'www/0.15/logfile'),
         ('cszo-logfile-0.16', CSZO + 'meta/0.16/logfile')]
# this line should be used on CSZO instead:
#         'cszo-logfile-0.16']
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.16', CAO + 'milestones16'),
#         ('cdo-milestones-0.16', CDO + 'milestones-0.16.txt'),
         ('cln-milestones-0.16', CLN + 'meta/0.16/milestones'),
#         ('rhf-milestones-0.14', RHF + 'meta/crawl-0.14/milestones'),
         ('cbro-milestones-0.16', CBRO + 'meta/0.16/milestones'),
#         ('ckr-milestones-0.15', CKR + 'www/0.15/milestones'),
         ('cszo-milestones-0.16', CSZO + 'meta/0.16/milestones')]
# this line should be used on CSZO instead:
#         'cszo-milestones-0.16']
