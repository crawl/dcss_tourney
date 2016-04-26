<%
   from crawl_utils import XXX_TOURNEY_BASE
   from test_data import USE_TEST
   version = '0.18'
   year    = '2016'
   title   = "Crawl %s Tournament Information" % version
 %>
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>${title}</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>
  <body class="page_back">
    <div class="page information">
      %if not USE_TEST:
        <%include file="toplink.mako"/>
      %endif
      <div class="page_content">
        <div class="heading">
          <h1>${title}</h1>
          <p class="fineprint">
            Tournament starts on <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20160506T20">May 6, ${year} at 20:00 UTC</a>, and ends on
            <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20160522T20">May 22, ${year} at 20:00 UTC</a>.
          </p>
        </div>
        <hr>

        <div class="content">
          <p>
            Hello all! Welcome to the rules for the
            ${version} Dungeon Crawl Stone Soup Tournament, running from <b><a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20160506T20">20:00 UTC Friday 6 May</a></b> to <b><a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20160522T20">20:00 UTC Sunday 22 May</a></b>. All version ${version} games played fully during this time period on any of the <a href="https://crawl.develz.org/wordpress/howto">public servers</a> will automatically count for the tournament.
          </p>

          <p>
            Participants in the tournament may form clans of six or
            fewer players. If you wish to join or captain a clan, see the <a href="#clans">Clans</a> section below.
          </p>

          <p>
            The <a href="#scoring">Scoring</a> section contains the full details of how to earn tournament points. The <a href="#banners">Banners</a> section has a list of additional special achievements.
          </p>

          <p>
            The <a href="#changes">Changes</a> section has a list of
            rule changes since the previous tournament.
          </p>

          <p>
            Once the tournament has started, the <a href="overview.html">Tournament Leaderboard</a> will contain the current results. (Some scores might briefly appear on this page before tournament start as we test the tournament scripts, but they are just for testing.)
          </p>

          <p>
            Have fun playing Crawl!
          </p>

          <hr>
          <a name="clans"></a>
          <h2>Clans</h2>

To become a member of a clan, you
            need to add a line to the top of one of your <b>version ${version}</b> rcfiles
            like this:
          </p>

          <pre>
# TEAMCAPTAIN nameofcaptain</pre>

          <p>
            This should be the very first line of your rcfile, with no
            blank lines or comments appearing before this line. The #
            is important to make sure Crawl doesn't try to parse the
            team data as an option.
          </p>

          <p>
            The team captain must have the name of her team and the
            other team members in one of her <b>version ${version}</b> rcfiles, like this:
          </p>

          <pre>
# TEAMNAME nameofteam
# TEAMMEMBERS player1 player2 player3 player4 player5</pre>

          <p>
            Again, these lines should be the very first two lines in
            the team captain's rcfile, with no blank lines or anything
            else appearing before these lines.
          </p>

          <p>
            <span>Note:</span> The team captain should <b>not</b>
            include a TEAMCAPTAIN line in her rcfile.
          </p>

          <div class="inset">
            <p>
              <span class="inline_heading">Note:</span> clan membership lines
              can be added to your ${version} rcfile on <b>any</b> of the
              public servers. If you add clan membership lines to more than
              one rcfile, then the rcfile on the server earliest in the list
              CAO, CBRO, CDO, CPO, CUE, CWZ, CXC, LLD will take
              precedence.
            </p>
          </div>

          <p>
            Clan names must contain only alphanumeric characters, underscores,
            and hyphens. Underscores will be converted into spaces. Once a
            player's username is in the captain's rcfile and the captain's
            username is in the player's rcfile and the tourney scripts notice
            this, the players will be in the same clan. The tourney scripts
            check for updates to rcfiles once every four hours.
          </p>

          <p>
            Clans may be changed by adding or removing players at any time
            until <b><a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20160513T20">20:00
            UTC Friday 13 May</a></b>, after which clans will be
            frozen.
          </p>

          <hr>

          <a name="scoring"></a>
          <h2>Scoring</h2>
          <hr>
          <div>
            <h3>GENERAL SCORING</h3>
            <h5>WINS</h5>
            <p>
              <span>100 points</span> for a player's first win. (Since winning
              is kind of the goal.)
            </p>

            <p>
              <span>50 points</span> for a player winning two characters of
              different species and backgrounds at some point during the tourney.
            </p>
            <h5>RUNES</h5>
            <p><span>24/N points</span> (rounded up) each time you find a
            type of rune for the Nth time. (So the first silver rune you
            find is worth 24 points, the second silver rune is worth 12 points, the
            third silver rune is worth 8 points, and so on.)</p>
            <h5>GODS</h5>
            <p>
              <span>10 points</span> the first time you reach full (******)
              piety with each god without having worshipped any
              other god first that game.
            </p>
            <h5>BRANCHES</h5>
            <p>
              <span>5 points</span> the first time you enter each branch or
              portal vault or reach the end of a multi-level branch.
            </p>
            <h5>UNIQUES</h5>
            <p><span>5 points</span> the first time you kill each
              unique.</p>

            <p><span>50-20-10 points</span> for the players with the most distinct
            uniques killed; ties broken by who gets that number first.</p>
            <h5>HIGH SCORES</h5>
            <p>
              <span>5 points</span> per high score in a species/background combination
              (HuFi, not just Hu).
            </p>

            <p>
              <span>5 additional points</span> for each high score in a
              species/background combination that is attained by a win.
            </p>

            <p><span>20 points</span> per high score in a species.</p>

            <p><span>10 points</span> per high score in a background.</p>

          </div>

          <hr>

          <div>
            <h3>SPECIES/BACKGROUND/GOD WINS</h3>
            <p>
              Wins with species, backgrounds, or gods that have been won fewer times in the tournament so far relative to other species, backgrounds, or gods are worth more points:
            </p>
            <p>
              <span>2*(52+T)/(2+S) points</span> (rounded up) for a win with a given species if T is the total number of games won in the tournament before the start of the win in question and S of those T were with the given species. If a player wins the same species multiple times, she only gets the largest value of this bonus among the wins, not the sum.

              For example, if there have been 10 games won prior to the start of the win in question and 2 of them were with the same species, then the
              win will be worth 2*(52+10)/(2+2) = 31 additional points.
            </p>
            <p>
              <span>(48+T)/(2+B) points</span> (rounded up) for a win with a given background if T is the total number of games won in the tournament before the start of the win in question and B of those T were with the given background. If a player wins the same background multiple times, she only gets the largest value of this bonus, not the sum.
            </p>
            <p>
              <span>1.5*(46+T)/(2+G) points</span> (rounded up) for a win with a given god if T is the total number of games won in the tournament before the start of the win in question and G of those T were with the given god. If a player wins with the same god multiple times, she only gets the largest value of this bonus, not the sum. For purposes of these points we say that a player wins with a god if she reaches full (******) piety with that god without worshipping any other god first. Two gods (Gozag and Xom) do not have the usual ****** piety system; to get the points for these gods, you must never worship another god during the game. For "No God", you must never worship a god.
            </p>
            <p>
              In addition, certain randomly chosen species/background combinations will be worth more points for the first eight players to win them:
            </p>
            <p>
              <span>75 bonus points</span> for winning <a href="#nemelex_choice">NEMELEX' CHOICE</a> characters. The first Nemelex' Choice combo is chosen at the start of the tournament, and after that each one is chosen when the previous one is won for the first time. Each combo remains valid until it has been won eight times. The species/background combinations are chosen by Nemelex from those with at most fifteen online wins.
            </p>
            <div class="inset">
              <p>
                The current values of the bonus for each species, background, or god
                will be
                listed on the "Species/Backgrounds/Gods" page. The current Nemelex' Choice combo as well as all past combos will be listed at the top of the "Overview" page.
              </p>
            </div>

            <div class="inset">
              <p>
                <span class="inline_heading">Important note for scoring:</span> The function f(x) = 800 * log<sub>2</sub>(1 + x / 800) will be applied to the total number of points each player or clan attains in this section. This means that the points in this section are worth less and less as you earn more of them! For example, f(800) = 800 and f(2400) = 1600, so points between 800 and 2400 are worth half as much as points between 0 and 800 (on average).
              </p>

              <p>
                Also, for clan scoring, if a clan has multiple wins for the same species,
                background, or god, only the largest value of the bonus among the
                wins is used, not the sum.
              </p>
            </div>
          </div>

          <hr>

          <div>
            <h3>SPEEDRUNS AND STREAKS</h3>
            <h5>RACES</h5>
            <p><span>200-100-50 points</span> for first win scored.</p>
            <p><span>200-100-50 points</span> for first 15-rune victory.</p>
            <p>
              <span>100 bonus points</span> for the win with the last
              starting time (among tournament wins) in the tournament.
            </p>
            <h5>PERSONAL RECORDS</h5>
            <p><span>5,000,000/turncount points</span> for each player's fastest win (by turncount).</p>
            <p><span>1,250,000/duration points</span> for each player's fastest win (by realtime, measured in seconds).</p>
            <p><span>score/120,000 points</span> for each player's highest scoring winning game.</p>
            <p><span>100*length points</span> for each player's longest streak of length at least 2, where length of
              a streak is defined as min(number of distinct species used, number
              of distinct backgrounds used).</p>
            <div class="inset">
              <p>
                Every game in a streak must be the first game you start after
                winning the previous game in the streak. This
                will always be the case if you play all your games on
                one server.
              </p>

              <p>
                If you are playing on multiple servers
                simultaneously, note that you cannot start game A and
                game B concurrently on two servers and win both in
                succession to earn streak points. You can however have
                multiple streaks in progress simultaneously.
              </p>
            </div>
          </div>

          <hr>

          <div>
            <h3>OTHER SPECIAL ACHIEVEMENTS</h3>
            <p>
            These points are only granted once per player per tournament.
            </p>
            <p>
              <span>50 points</span> for winning without visiting Lair, Orc, or
              the Vaults (<a href="#lord_of_darkness">LORD OF DARKNESS</a>
              banner III).
            </p>
            <p><span>25 points</span> for a game in which you enter Tomb for the first time after picking up the Orb of Zot and then get the golden rune (<a href="#natures_ally">NATURE'S ALLY</a> banner III).
            </p>

            <p><span>25 points</span> for a game in which you get six runes before entering the Depths (<a href="#vow_of_courage">VOW OF COURAGE</a> banner III).
            </p>

            <p>
              <span>25 points</span> for a game in which you get your first rune (which cannot be the slimy or abyssal runes) without the use of any potions or scrolls (<a href="#the_ascetic">THE ASCETIC</a> banner III).
            </p>

            <p>
              <span>25 points</span> for a game in which you find the iron rune before entering Pandemonium or any branch of the dungeon containing any other rune (<a href="#avarice">AVARICE</a> banner III). This means that only Temple, Lair, Orc, Elf, Depths, Abyss, Hell, and Dis can be entered.
            </p>

            <p>
              <span>25 points</span> for winning the game before reaching experience level 19 (and without using Ru's Sacrifice Experience ability) (<a href="#ruthless_efficiency">RUTHLESS EFFICIENCY</a> banner III).
            </p>

          </div>

          <hr>

          <div>
            <h3>CLAN POINTS ONLY</h3>

            <p>
              These get you clan points but do not get you points
              toward the individual prize, encouraging
              specialization within clans but making the hypothetical
              "Best Crawl Player" award based on more "real"
              metrics.
            </p>

            <p>
              <span>100-50-20 clan points</span> for deepest level reached in a Ziggurat. Completing a Ziggurat level (for instance exiting to the dungeon from Zig:20) is also noted and is better than merely reaching the level. Ties are broken by who reaches/exits the Ziggurat level first.
            </p>

            <p>
              <span>5*D clan points</span> for reaching Zig:D. (Only the
              best Ziggurat attempt in each clan counts.) Leaving the
              Ziggurat safely counts as an extra level.
            </p>

            <p><span>100-50-20 clan points</span> for winning a game with the
            lowest XL. Ties are broken by who finishes the game first.
            </p>

            <p><span>50-20-10 clan points</span> for lowest XL at which a
            rune is picked up, not including the abyssal and slimy runes. Ties
            are broken by who picked up the rune first.
            </p>

            <p>
              <span>50-20-10 clan points</span> for the "Most Unique Deaths"
              trophy: Killed by the most distinct uniques. Ties are broken by
              who reaches that number first.
            </p>

            <p>
              <span>20 clan points</span> for winning a character that was
              not previously won in the tournament.
            </p>

            <p><span>2 clan points</span> per player ghost killed while playing, up to a maximum of 100 ghosts killed by each player.</p>

            <p>
              <span>N clan points</span> per ghost kill after dying, where
              N is the dying character's XL minus 5. (No points are awarded if the dying character is XL 5 or lower.)
            </p>

            <p>
              <span>200-100-50 clan points</span> for the players with the most high
              scores in species/background combinations.
            </p>

            <p>
              <span>200-100-50 clan points</span> for the <b>clans</b> with the most
              high scores in species/background combos.
            </p>

            <p>
              <span>100-50-20 clan points</span> for the <b>clans</b> with the most
              distinct uniques killed; ties broken by who gets that number first.
            </p>

          </div>

          <hr>

          <div>
            <h3>CLAN SCORING</h3>

            <p>
              Sum total of all individual points with the exception of
              "Species/Background/God wins" points (for which only the largest value of the bonus among the clan's wins is used, as described in that section), plus the
              "Clan points only" awards above.
            </p>

            <p>
              Six players or fewer per clan.
            </p>
          </div>

          <hr>

          <div>
            <h3>CONDUCT</h3>
            <p>
              Please do not do anything that would give you an unfair competitive advantage over other players or clans. This includes stuff like scumming crash-on-demand bugs or running bots on your own account for speedrun points &ndash; just remember that the objective here is to have fun. (You are welcome to run bots on their own accounts in the tourney, though as always on online servers you should be careful not to hammer the CPU with them. Also, bot wins will not be displayed on lists of fastest wins.)
            </p>
          </div>

          <div>
            <hr>
            <a name="banners"></a>
            <h2>BANNERS</h2>

            <div>
              <p>
                The gods of DCSS will reward players for certain achievements. Each god gives out three banners, each one building on the previous to heap even more glory on the player. These banners are not worth tournament points except where explicitly stated, but the highest banner received from each god will be displayed on the player's page.
              </p>
            </div>

            <hr>
          </div>
          <div class="banner-desc">
            <div>
              <img src="images/banner_ashenzari1.png"
                   alt="The Explorer"
                   title="The Explorer"
                   width="170" height="58"
                   >
              <p>
                Ashenzari thinks that an <a name="explorer">EXPLORER</a> should be be busy looking for runes of Zot.
              <br>
                I: Enter a branch of the dungeon that contains a rune.
              <br>
                II: Find 5 distinct runes over the course of the tourney.
              <br>
                III: Find 17 distinct runes over the course of the tourney. (Only two of the four runes in Shoals/Snake/Spider/Swamp are available in a given game, so this requires multiple games.)
            </div>

            <hr>

            <div>
              <img src="images/banner_beogh1.png"
                   alt="The Heretic"
                   title="The Heretic"
                   width="170" height="58"
                   >
              <p>
                Beogh hates all the other gods and
                admires <a name="heretic">HERETICS</a> who go out of their way
                to incur their wrath. The good gods (Elyvilon, the Shining One,
                and Zin) and Ru are insufficiently wrathful, so abandoning them
                does not impress Beogh. Any god except the good gods, Ru, and
                Beogh are hence applicable for this banner.

              <br>
                I: Abandon and mollify an applicable god.
              <br>
                II: Over the course of the tournament, abandon and mollify
                three applicable gods.
              <br>
                III: Over the course of the tournament, abandon and mollify
                nine applicable gods.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_cheibriados1.png"
                   alt="Slow and Steady"
                   title="Slow and Steady"
                   width="170" height="58"
                   >
              <p>
                Cheibriados believes in being
                <a name="slow_and_steady">SLOW AND STEADY</a> and will
                so recognize players who are careful enough to excel in
                consecutive games.
              <br>
                I: Reach experience level 9 in two consecutive games.
              <br>
                II: Achieve a two-win streak.
              <br>
                III: Achieve a four-win streak with four distinct species and four distinct backgrounds.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_dithmenos1.png"
                   alt="The Politician"
                   title="The Politician"
                   width="170" height="58"
                   >
              <p>
                Dithmenos appreciates the subtlety of a
                <a name="politician">POLITICIAN</a> and will
                thus reward any player who steals a high score from another player.
              <br>
                I: Steal a combo high score that was previously of at least 1,000 points.
              <br>
                II: Steal a combo high score for a previously won combo.
              <br>
                III: Steal a species or background high score that was previously of at least 10,000,000 points.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_elyvilon1.png"
                   alt="The Pious"
                   title="The Pious"
                   width="170" height="58"
                   >
              <p>
                Elyvilon thinks it's important to check out what all
                the gods have to offer and thus will
                recognize as <a name="pious">PIOUS</a> any
                player who becomes the Champion (******) of as many gods
                as possible.
              <br>
                I: Become the champion of any god.
              <br>
                II: Become the champion of five different gods over the course of the tournament.
              <br>
                III: Become the champion of thirteen different gods over the course of the tournament.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_fedhas1.png"
                   alt="Nature's Ally"
                   title="Nature's Ally"
                   width="170" height="58"
                   >
              <p>
                Fedhas thinks that the Crypt and the Tomb are abominations against nature and will bestow the title of <a name="natures_ally">NATURE'S ALLY</a> on a player who works towards destroying them.
              <br>
                I: Enter the Crypt.
              <br>
                II: Get the golden rune.
              <br>
                III: Enter Tomb for the first time after picking up the Orb of Zot, and then get the golden rune (+25 tournament points).
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_gozag1.png"
                   alt="Avarice"
                   title="Avarice"
                   width="170" height="58"
                   >
              <p>
                Gozag wants players to demonstrate their <a name="avarice">AVARICE</a> by collecting certain valuable metals.
              <br>
                I: Find 1000 gold in a single game.
              <br>
                II: Find the silver rune.
              <br>
                III: Find the iron rune before entering Pandemonium or any branch of the dungeon containing any other rune (+25 tournament points). This means that only Temple, Lair, Orc, Elf, Depths, Abyss, Hell, and Dis can be entered.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_jiyva1.png"
                   alt="Gelatinous Body"
                   title="Gelatinous Body"
                   width="170" height="58"
                   >
              <p>
                Jiyva thinks that it is important to be flexible and will gift
                players who excel with at least 5 distinct
                species and at least 5 distinct backgrounds with a
                <a name="gelatinous_body">GELATINOUS BODY</a>.
              <br>
                I: Reach experience level 9 with at least 5 distinct species and at least 5 distinct backgrounds.
              <br>
                II: Get a rune with at least 5 distinct species and at least 5 distinct backgrounds.
              <br>
                III: Win with at least 5 distinct species and at least 5 distinct backgrounds.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_kikubaaqudgha1.png"
                   alt="Lord of Darkness"
                   title="Lord of Darkness"
                   width="170" height="58"
                   >
              <p>
                Kikubaaqudgha wants players to demonstrate their mastery over
                the forces of darkness without delay, and will recognise a player
                who shows disdain for the Lair as
                a <a name="lord_of_darkness">LORD OF DARKNESS</a>.
              <br>
                I: Reach the last level of the Orcish Mines without having entered the Lair.
              <br>
                II: Reach the last level of the Depths without having entered the Lair.
              <br>
                III: Win a game without having entered the Lair, the Orcish
                Mines, or the Vaults (+50 tournament points).
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_lugonu1.png"
                   alt="Spiteful"
                   title="Spiteful"
                   width="170" height="58"
                   >
              <p>
                Lugonu hates all the other gods. At the moment, Lugonu is
                especially <a name="spiteful">SPITEFUL</a> towards Ru and
                admires those who make sacrifices to Ru and then abandon Ru's
                worship.
              <br>
              I: Become the champion of Ru (the first step towards betraying Ru).
              <br>
              II: After becoming the champion of Ru, abandon Ru and become the
              champion of a different god.
              <br>
              III: Win a game in which you become the champion of Ru and then
              abandon Ru before entering any branches other than the Temple and
              the Lair.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_makhleb1.png"
                   alt="Speed Demon"
                   title="Speed Demon"
                   width="170" height="58"
                   >
              <p>
                Makhleb wants to see bloodshed as quickly as possible and
                will give players the bare minimum of time needed to prove themselves as <a name="speed_demons">SPEED DEMONS</a>. Makhleb isn't interested in digging (and has cacodemons for that), so formicids are not eligible for the first tier of this banner.
              <br>
I: Reach D:15 in 27 minutes as a non-formicid.
              <br>
II: Find a rune in 81 minutes.
              <br>
III: Win the game in 3 hours.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_nemelex1.png"
                   alt="Nemelex' Choice"
                   title="Nemelex' Choice"
                   width="170" height="58"
                   >
              <p>
                Nemelex Xobeh wants to see players struggle and loves
                randomness, and so will give the
                <a name="nemelex_choice">NEMELEX' CHOICE</a> award
                to players who persevere with one of several combos
                randomly chosen and announced throughout the
                tournament.
              <br>
                I: Reach experience level 9 with a Nemelex' choice combo.
              <br>
                II: Get a rune with a Nemelex' choice combo.
              <br>
                III: Be one of the first 8 players to win a given Nemelex' choice combo (+75 tournament points).
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_okawaru1.png"
                   alt="The Conqueror"
                   title="The Conqueror"
                   width="170" height="58"
                   >
              <p>
                Okawaru is all about winning, all the time, and thus
                will recognize as <a name="the_conqueror">THE CONQUEROR</a> any player who
                is victorious.
              <br>
                I: Reach experience level 13.
              <br>
                II: Win a game.
              <br>
                III: Win a game in under 50000 turns.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_qazlal1.png"
                   alt="The Prophet"
                   title="The Prophet"
                   width="170" height="58"
                   >
              <p>
                Qazlal demands fervent worship! Accordingly, Qazlal will only
                recognize as <a name="the_prophet">THE PROPHET</a> those who dedicate themselves to
                Invocations.
              <br>
                I: Enter the Lair of Beasts with an Invocations title.
              <br>
                II: Win the game with an Invocations title.
              <br>
                III: Over the course of the tournament, win with three different Invocations titles.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_ru1.png"
                   alt="The Ascetic"
                   title="The Ascetic"
                   width="170" height="58"
                   >
              <p>
                Ru will recognize as <a name="the_ascetic">THE ASCETIC</a> those who sacrifice all use of potions and scrolls for a time.
              <br>
                I: Reach the Ecumenical Temple without using any potions or scrolls.
              <br>
                II: Reach the last level of the Lair of Beasts without using any potions or scrolls.
              <br>
                III: Find your first rune of a game without using any potions or scrolls (+25 tournament points). This rune cannot be the slimy or abyssal rune: Ru requires you to undergo this sacrifice for longer.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_sif1.png"
                   alt="Lorekeeper"
                   title="Lorekeeper"
                   width="170" height="58"
                   >
              <p>
                Sif Muna thinks that a
                <a name="lorekeeper">LOREKEEPER</a> doesn't need skill, just knowledge of spells. Ashenzari has a different viewpoint on this subject, so Sif Muna has banned Ashenzari worshippers from receiving this banner.
              <br>
                I: Reach the last level of the Lair as a non-formicid without raising any skill to 13.
              <br>
                II: Win without raising any skill to 20.
              <br>
                III: Win without raising any skill to 13.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_the_shining_one1.png"
                   alt="Vow of Courage"
                   title="Vow of Courage"
                   width="170" height="58"
                   >
              <p>
                The Shining One thinks each player should take a
                <a name="vow_of_courage">VOW OF COURAGE</a> and face great terrors before entering the Depths.
              <br>
                I: Kill Sigmund before entering the Depths.
              <br>
                II: Get four runes before entering the Depths.
              <br>
                III: Get six runes before entering the Depths (+25 tournament points).
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_trog1.png"
                   alt="Brute Force"
                   title="Brute Force"
                   width="170" height="58"
                   >
              <p>
                Trog thinks players should rely on
                <a name="brute_force">BRUTE FORCE</a> and persevere without worshipping any god at all. Demigods cannot win Trog's praise for this, since they do not have a choice in the matter.
              <br>
I: Reach the last level of the Lair as a non-demigod without worshipping a god.
              <br>
II: Find a rune as a non-demigod without worshipping a god.
              <br>
III: Win a game as a non-demigod without worshipping a god.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_vehumet1.png"
                   alt="Ruthless Efficiency"
                   title="Ruthless Efficiency"
                   width="170" height="58"
                   >
              <p>
                Vehumet values focus and dedication, and will reward those who
                demonstrate
                <a name="ruthless_efficiency">RUTHLESS EFFICIENCY</a> by achieving their goals without stopping to gain unnecessary experience. Followers of Ru who sacrifice their experience are inefficient and will be disqualified from this banner.
              <br>
                I: Reach the last level of the Lair as a non-formicid before reaching experience level 12.
              <br>
                II: Find a rune before reaching experience level 14.
              <br>
                III: Win the game before reaching experience level 19 (+25 tournament points).
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_xom1.png"
                   alt="Descent into Madness"
                   title="Descent into Madness"
                   width="170" height="58"
                   >
              <p>
                Xom is always looking for entertainment and thinks it would be
                hilarious to watch a player's
                <a name="descent_into_madness">DESCENT INTO MADNESS</a>
                into the Abyss or through a ziggurat.
              <br>
                I: Enter the Abyss.
              <br>
                II: Reach the 10th floor of a ziggurat.
              <br>
                III: Leave a ziggurat from its lowest floor.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_yredelemnul1.png"
                   alt="The Harvest"
                   title="The Harvest"
                   width="170" height="58"
                   >
              <p>
                Yredelemnul demands that you kill as many uniques as possible and
                will recognise success by awarding
                <a name="the_harvest">THE HARVEST</a>.
              <br>
                I: Kill 32 distinct uniques over the course of the tournament.
              <br>
                II: Kill 52 distinct uniques over the course of the tournament.
              <br>
                III: Kill 72 distinct uniques over the course of the tournament.
              </p>
            </div>

            <hr>

            <div>
              <img src="images/banner_zin1.png"
                   alt="Angel of Justice"
                   title="Angel of Justice"
                   width="170" height="58"
                   >
              <p>
                Zin will give the
                <a name="angel_of_justice">ANGEL OF JUSTICE</a> award to any
                player who attempts to cleanse Hell and Pandemonium.
              <br>
                I: Enter either Pandemonium or any branch of Hell.
              <br>
                II: Kill at least one unique pan lord and at least one unique hell lord over the course of the tournament.
              <br>
                III: Kill all four unique pan lords, all four unique hell
                lords, and the Serpent of Hell (at least once) over the course
                of the tournament.
              </p>
            </div>
          </div>

          <hr style="clear: both">

          <div>
            <a name="changes"></a>
            <h2>CHANGED RULES</h2>

            <hr>
            <div class="fineprint">
              <p>
                Some rules have been changed from the 0.17 tournament held in
                November 2015. This is a list of rules differences.
              </p>

              <p><span class="removed">[REMOVED]</span>
                flags rules that existed in the 0.17 tournament and are gone in
                this tournament.</p>

              <p><span class="added">[NEW]</span>
                flags rules that are new to this tournament.</p>

              <p><span class="changed">[CHANGED]</span>
                flags rules that have been modified for this
                tournament. To compare
                changed rules with the rules in the 0.17 tournament, see
                the <a href="http://dobrazupa.org/tournament/0.17/">old
                rules</a>.
              </p>
            </div>

            <hr>

	    <!--
            <p class="added">
              <span>Beogh's</span> <span>SAINT</span> clan banner has been
              reworked into the <span><a href="#heretic">HERETIC</a></span>
              banner.
              <span class="added">[NEW]</span>
            </p>

            <p class="changed">
              The third tier of <span>Zin's</span> <span>ANGEL OF
              JUSTICE</span> banner now requires the player to kill the Serpent
              of Hell at least once.
              <span class="changed">[CHANGED]</span>
            </p>

            <p class="removed">
              <span>50-20-10 clan points</span> for finishing a game with the
              highest value of AC+EV.
              <span class="removed">[REMOVED]</span>
            </p>
	    -->
          </div>

          <hr>
          <div>
            <h2>CREDITS</h2>

            <p>
              We'd like to thank:
            </p>
            <p>
              <span>greensnark</span> for writing the original tournament
              scripts that have been adapted for use in this tournament.
            </p>
            <p>
              <span>|amethyst</span> for hosting the tournament scripts.
            </p>
            <p>
              <span>Wensley</span>, <span>ChrisOelmueller</span>, and <span>Grunt</span> for creating the banner images.
            </p>
            <p>
              <span>many others</span> for helping to create these rules!
            </p>
          </div>

        </div> <!-- Content -->
      </div>
    </div>
  </body>
</html>
