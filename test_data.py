from crawl_utils import LOCAL_TEST
CDO = 'http://crawl.develz.org/'
CAO = 'http://crawl.akrasiac.org/'

USE_TEST = False

TEST_YEAR = USE_TEST and '2012'
TEST_VERSION = USE_TEST and '0.11'
TEST_START_TIME = USE_TEST and (TEST_YEAR + '0801')
TEST_END_TIME   = USE_TEST and (TEST_YEAR + '0901')
TEST_HARE_START_TIME = USE_TEST and (TEST_YEAR + '0831')
TEST_LOGS = USE_TEST and [ LOCAL_TEST and ('cao-logfile-git', CAO + 'logfile-git')
         or 'cao-logfile-git',
         ('cdo-logfile-svn', CDO + 'allgames-svn.txt') ]
TEST_MILESTONES = USE_TEST and [ LOCAL_TEST and ('cao-milestones-git', CAO + 'milestones-git')
               or 'cao-milestones-git',
               ('cdo-milestones-svn', CDO + 'milestones-svn.txt') ]
