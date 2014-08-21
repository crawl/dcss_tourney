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
TEST_VERSION = USE_TEST and '0.15'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0401')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0408')
TEST_CLAN_DEADLINE = (USE_TEST and
                     datetime.datetime(2012, 5, 1, 0)) # May 1, 00:00
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0407')
TEST_LOGS = USE_TEST and [
         ('cao-logfile-0.15', CAO + 'logfile15'),
#         ('cdo-logfile-0.15', CDO + 'allgames-0.15.txt'),
         ('cln-logfile-0.15', CLN + 'meta/0.15/logfile'),
#         ('rhf-logfile-0.14', RHF + 'meta/crawl-0.14/logfile'),
         ('cbro-logfile-0.15', CBRO + 'meta/0.15/logfile'),
         ('ckr-logfile-0.15', CKR + 'www/0.15/logfile'),
         ('cszo-logfile-0.15', CSZO + 'meta/0.15/logfile')]
# this line should be used on CSZO instead:
#         'cszo-logfile-0.15']
TEST_MILESTONES = USE_TEST and [
         ('cao-milestones-0.15', CAO + 'milestones15'),
#         ('cdo-milestones-0.15', CDO + 'milestones-0.15.txt'),
         ('cln-milestones-0.15', CLN + 'meta/0.15/milestones'),
#         ('rhf-milestones-0.14', RHF + 'meta/crawl-0.14/milestones'),
         ('cbro-milestones-0.15', CBRO + 'meta/0.15/milestones'),
         ('ckr-milestones-0.15', CKR + 'www/0.15/milestone'),
         ('cszo-milestones-0.15', CSZO + 'meta/0.15/milestones')]
# this line should be used on CSZO instead:
#         'cszo-milestones-0.15']
