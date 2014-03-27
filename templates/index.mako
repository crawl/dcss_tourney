<%
   from crawl_utils import XXX_TOURNEY_BASE
   from test_data import USE_TEST
   version = '0.14'
   year    = '2014'
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
            Tournament starts on <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20140411T20">Apr 11, ${year} at 20:00 UTC</a>, and ends on
            <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20140427T20">Apr 27, ${year} at 20:00 UTC</a>.
          </p>
        </div>
        <hr>

        <div class="content">
          <p>
            Hello all! Welcome to the rules for the
            ${version} Dungeon Crawl Stone Soup Tournament. The simple part:
            Play on one of the <b>five</b> public servers (<a href="http://crawl.akrasiac.org">crawl.akrasiac.org</a>,
            <a href="http://crawl.develz.org">crawl.develz.org</a>,
            <a href="http://crawl.lantea.net:8080">crawl.lantea.net</a>,
            <a href="http://crawl.s-z.org">crawl.s-z.org</a>,
            or <a href="http://rl.heh.fi:8080">rl.heh.fi</a>)
            and all of
            your Crawl ${version} games that <b>start after <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20140411T20">20:00 UTC on
            Apr 11</a></b> and <b>end before <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20140427T20">20:00 UTC on Apr 27</a></b> will
            count toward the tournament.
          </p>

          <div class="inset">
            <p>
              <span class="inline_heading">Note:</span> One of the servers, RHF, does not currently have 0.13 set up. Until it gets 0.13, you will be unable to use this server for tourney purposes; please use one of the other four servers instead.
            </p>
          </div>

          <p>
            For players who participated in previous
            tournaments, please look at
            the <a href="#changes">Changes</a> section for a list of
            rule changes.
          </p>

          <p>
            Participants in the tournament may form clans of six or
            fewer players. If you wish to be a member of a clan, you
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
              <span class="inline_heading">Note:</span> clan membership lines can be added to your ${version} rcfile on <b>any</b> of the public servers.
              If you add clan
              membership lines to more than one rcfile, then the rcfile on
              the server earliest in the list CSZO, CAO, CDO, CLN, RHF will take
              precedence.
            </p>
          </div>

          <p>
            Clan names must contain only alphanumeric characters,
            underscores, and hyphens. Underscores will be converted into
            spaces. Once a player's username is in
            the captain's rcfile and the captain's username is in the
            player's rcfile and the tourney scripts notice this, the
            players will be in the same clan. The tourney scripts only check for
            updates to non-CSZO rcfiles once every four hours, so if
            you are impatient about this then you should edit your CSZO rcfile instead.
          </p>

          <p>
            Clans may be changed by adding or removing players at any
            time until <b><a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20140419T19">19:00 UTC on Apr 19</a></b>, after which clans will be
            effectively frozen.
          </p>

          <hr>

          <div>
            <h2>WINS</h2>
            <p>
              <span>100 points</span> for a player's first win. (Since winning
              is kind of the goal.)
            </p>

            <p>
              <span>50 points</span> for a player winning two characters of
              different species and backgrounds at some point during the tourney.
            </p>

            <p>
              <span>60 extra points</span> for each consecutive (streak) win
              by a player with a species that has not 
	      previously been a streak win for that player.
            </p>
            <p>
              <span>30 extra points</span> for each consecutive (streak) win
              by a player with a background that has not 
	      previously been a streak win for that player.
            </p>

            <div class="inset">
              <p>
                For every game in a streak, the start time of the game
                must be later than the previous game's end time. This
                will always be the case if you play all your games on
                one server.
              </p>

              <p>
                If you're playing on multiple servers
                simultaneously, note that you cannot start game A and
                game B concurrently on two servers and win both in
                succession to earn streak points.
              </p>
            </div>
          </div>

          <hr>

          <div>
            <h2>SPECIES/BACKGROUND/GOD WINS</h2>
            <p>
              <span>2*(48+T)/(2+S) points</span> (rounded up) for a win with a given species if T is the total number of games won in the tournament before the start of the win in question and S of those T were with the given species. If a player wins the same species multiple times, she only gets the largest value of this bonus among the wins, not the sum.

              For example, if there have been 10 games won prior to the start of the win in question and 2 of them were with the same species, then the
              win will be worth 2*(48+10)/(2+2) = 29 additional points.
            </p>
            <p>
              <span>(52+T)/(2+B) points</span> (rounded up) for a win with a given background if T is the total number of games won in the tournament before the start of the win in question and B of those T were with the given background. If a player wins the same background multiple times, she only gets the largest value of this bonus, not the sum.
            </p>
            <p>
              <span>1.5*(38+T)/(2+G) points</span> (rounded up) for a win with a given god if T is the total number of games won in the tournament before the start of the win in question and G of those T were with the given god. If a player wins with the same god multiple times, she only gets the largest value of this bonus, not the sum. For purposes of these points we say that a player wins with a god if she reaches full (******) piety with that god without worshipping any other god first. For Xom, you must play a Chaos Knight and never abandon Xom. For "No God", you must never worship a god.
            </p>
            <div class="inset">
              <p>
	        For clan scoring, if a clan has multiple wins for the same species,
                background, or god, only the largest value of the bonus among the
                wins is used, not the sum.
	      </p>
            </div>
            <div class="inset">
              <p>
	        The current values of the bonus for each species, background, or god
                will be
                listed on the "Species/Backgrounds/Gods" page for your convenience.
	      </p>
            </div>
          </div>
          <hr>

          <div>
            <h2>SPECIAL WINS</h2>
	    <p><span>5,000,000/turncount points</span> for each player's fastest win (by turncount).</p>
            <p><span>1,250,000/duration points</span> for each player's fastest win (by realtime, measured in seconds).</p>
            <p><span>200-100-50 points</span> for first win scored.</p>
            <p><span>200-100-50 points</span> for first 15-rune victory.</p>
            <p><span>200-100-50 points</span> for longest streak of
              winning games, where "length" of 
	      a streak is defined as min(number of distinct species used, number 
	      of distinct backgrounds used).
              Ties are broken by the first to achieve the streak.
            </p>
            <p>
              <span>100 bonus points</span> for the win with the last
              starting time (among tournament wins) in the tournament.
            </p>
	    <p>
	      <span>50 bonus points</span> for a win without visiting
	      Temple, Lair, Orc, or the Vaults (<a href="#lord_of_darkness">LORD OF DARKNESS</a> banner III).
	    </p>
            <p>
              <span>75 bonus points</span> for winning <a href="#nemelex_choice">NEMELEX' CHOICE</a> characters. The first Nemelex' Choice combo is chosen at the start of the tournament, and after that each one is chosen when the previous one is won for the first time. Each combo remains valid until it has been won five times. The species/background combinations are chosen by Nemelex from those with fewer than eight online wins.
            </p>
          </div>

          <hr>

          <div>
            <h2>SPECIAL ACHIEVEMENTS</h2>

            <p><span>25 points</span> for each game in which you enter Tomb for the first time after picking up the Orb of Zot and then get the golden rune (<a href="#natures_ally">NATURE's ALLY</a> banner III).
            </p>

            <p><span>25 points</span> for each game in which you get four runes before entering D:14 (or below) in that game (<a href="#vow_of_courage">VOW OF COURAGE</a> banner III).
            </p>
          </div>

          <hr>

          <div>
            <h2>RUNES</h2>

            <p><span>30/N points</span> (rounded up) each time you find a 
            type of rune for the Nth time. (So the first silver rune you 
            find is worth 30 points, the second silver rune is worth 15 points, the 
            third silver rune is worth 10 points, and so on.)</p>
          </div>

          <hr>

          <div>
            <h2>HIGH SCORES</h2>
            <p><span>score/120,000 points</span> for each player's highest scoring winning game.</p>

            <p>
              <span>5 points</span> per high score in a species/background combination
              (HuWn, not just Hu).
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
            <h2>UNIQUES</h2>

            <p><span>5 points</span> the first time you kill each
              unique.</p>

            <p><span>50-20-10 points</span> for the players with the most unique 
	    uniques killed; ties broken by who gets that number first.</p>
          </div>

          <hr>

          <div>
            <h2> GODS </h2>
            <p>
              <span>10 points</span> the first time you reach full (******)
              piety with each god without having worshipped any
              other god first that game.
            </p>
          </div>

          <hr>

          <div>
            <h2> BRANCHES </h2>
            <p>
              <span>5 points</span> the first time you enter each branch or
              portal vault or reach the end of a multi-level branch.
            </p>
          </div>

          <hr>

          <div>
            <h2>CLAN POINTS ONLY</h2>

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

            <p><span>50-20-10 clan points</span> for finishing a game with the
            highest value of AC+EV. Ties are broken by who finishes the game
            first.
            </p>

            <p><span>50-20-10 clan points</span> for lowest XL at which a
            rune is picked up, not including the abyssal and slimy runes. Ties
	    are broken by who picked up the rune first.
	    </p>

            <p>
              <span>50-20-10 clan points</span> for the "Most Unique Deaths"
              trophy: Killed by the most unique uniques. Ties are broken by 
	      who reaches that number first.
            </p>

            <p>
              <span>20 clan points</span> for winning a character that was
              not previously won in the tournament.
            </p>

            <p><span>2 clan points</span> per player ghost killed while playing.</p>

            <p>
              <span>N clan points</span> per ghost kill after dying, where
              N is the dying character's XL minus 5.
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
              unique uniques killed; ties broken by who gets that number first.
            </p>

          </div>

          <hr>

          <div>
            <h2>CLAN SCORING</h2>

            <p>
              Sum total of all individual points with the exception of
              "Species/Background/God wins" points (for which only the largest value of the bonus among the clan's wins is used, as described in that section), plus the
	      "Clan points only" awards above.
            </p>

            <p>
              Six players or fewer per clan.
            </p>
          </div>

          <div>
            <hr>
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
                I: Enter a branch that contains a rune.
              <br>
                II: Find 5 distinct runes over the course of the tourney.
              <br>
                III: Find 17 distinct runes over the course of the tourney.
            </div>

	    <hr>

            <div>
	      <img src="images/banner_beogh1.png"
                   alt="The Saint"
                   title="The Saint"
                   width="170" height="58"
                   >
              <p>
	        Beogh thinks that the only thing more important than
                having friends is dominating your friends, and will recognize
                as a <a name="saint">SAINT</a> the player with the highest
                tournament score on each clan, especially if that player
                leads her clan to glory.
              <br>
                I: Have the highest score in your clan.
              <br>
                II: Have the highest score in a clan that is ranked in the top 27.
              <br>
                III: Have the highest score in a clan that is ranked in the top 5.
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
                I: Enter the Vestibule of Hell without having entered the Lair.
              <br>
                II: Get a rune without having entered the Lair.
              <br>
                III: Win a game without having entered the Temple, the Orcish Mines, the Lair, or the Vaults (+50 tournament points).
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_lugonu1.png"
                   alt="The Unbeliever"
                   title="The Unbeliever"
                   width="170" height="58"
                   >
              <p>
                Lugonu hates all the other gods and admires <a name="unbelievers">UNBELIEVERS</a> who persevere without worshipping any god at all. Demigods cannot win Lugonu's praise for this, since they do not have a choice in the matter.
              <br>
I: Reach the end of the Lair as a non-demigod without worshipping a god.
              <br>
II: Find a rune as a non-demigod without worshipping a god.
              <br>
III: Win a game as a non-demigod without worshipping a god.
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
                will give players just 27
                minutes to prove themselves as <a name="speed_demons">SPEED DEMONS</a>.
              <br>
I: Reach D:14 in 27 minutes.
              <br>
II: Enter the Vestibule of Hell in 27 minutes.
              <br>
III: Reach D:27 in 27 minutes.
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
                III: Be one of the first 5 players to win a given Nemelex' choice combo (+75 tournament points).
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
	      <img src="images/banner_sif1.png"
                   alt="Lorekeeper"
                   title="Lorekeeper"
                   width="170" height="58"
                   >
              <p>
                Sif Muna thinks that a
                <a name="lorekeeper">LOREKEEPER</a> doesn't need skill, just knowledge of spells. Ashenzari has a different viewpoint on this subject, so Sif Muna has banned Ashenzari worshippers from receiving this banner.
              <br>
                I: Reach the last level of the Lair without raising any skill to 13.
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
                <a name="vow_of_courage">VOW OF COURAGE</a> and not delay
                fighting for their runes.
              <br>
                I: Get a rune before entering D:14 (or below) in that game.
              <br>
                II: Get two runes before entering D:14 (or below) in that game.
              <br>
                III: Get four runes before entering D:14 (or below) in that game (+25 tournament points).
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_trog1.png"
                   alt="The Sniper"
                   title="The Sniper"
                   width="170" height="58"
                   >
              <p>
                Trog will recognize as
                <a name="the_sniper">THE SNIPER</a> any player
                who steals a high score from another player.
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
	      <img src="images/banner_vehumet1.png"
                   alt="Ruthless Efficiency"
                   title="Ruthless Efficiency"
                   width="170" height="58"
                   >
              <p>
                Vehumet values focus and dedication, and will reward those who
                demonstrate
                <a name="ruthless_efficiency">RUTHLESS EFFICIENCY</a> by achieving their goals within a (real-world) 27-hour time period.
              <br>
                I: Get a rune within 27 real-world hours of starting the game.
              <br>
                II: Win a game within 27 real-world hours of starting it.
              <br>
                III: Start and win two games within a single 27-hour time period.
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
                through a ziggurat.
              <br>
                I: Enter a ziggurat.
              <br>
                II: Reach the 14th floor of a ziggurat.
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
                I: Kill 28 distinct uniques over the course of the tournament.
              <br>
                II: Kill 48 distinct uniques over the course of the tournament.
              <br>
                III: Kill 68 distinct uniques over the course of the tournament.
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
                III: Kill all four unique pan lords and all four unique hell lords over the course of the tournament.
              </p>
            </div>
          </div>

          <hr style="clear: both">

          <div>
            <h2>CHANGED RULES</h2>
            <a name="changes"></a>

            <hr>
            <div class="fineprint">
              <p>
                Some rules have been changed from the 0.13 tournament held in October 2013. This is a list of rules differences.
              </p>

              <p><span class="removed">[REMOVED]</span>
                flags rules that existed in the 0.13 tournament and are gone in
                this tournament.</p>

              <p><span class="added">[NEW]</span>
                flags rules that are new to this tournament.</p>

              <p><span class="changed">[CHANGED]</span>
                flags rules that have been modified for this 
		tournament. To compare
                changed rules with the rules in the 0.13 tournament, see
                the <a href="http://dobrazupa.org/tournament/0.13/">old
                rules</a>.
              </p>
            </div>

            <hr>

            <p class="added">
              <span>25 points</span> for each game in which you enter Tomb for the first time after picking up the Orb of Zot and then get the golden rune (<a href="#natures_ally">NATURE's ALLY</a> banner III).
              <span class="added">[NEW]</span>
            </p>

            <p class="added">
              <span>25 points</span> for each game in which you get four runes before entering D:14 (or below) in that game (<a href="#vow_of_courage">VOW OF COURAGE</a> banner III).
              <span class="added">[NEW]</span>
            </p>

            <p class="changed">
              <span>Beogh</span> now only asks you to have the highest score in a clan that is ranked in the top 27 for the second tier of the <span><a href="#saint">SAINT</a></span> banner. (Used to require top 20.)
              <span class="changed">[CHANGED]</span>
            </p>

            <p class="changed">
              <span>Lugonu</span> has a <a href="#unbelievers">new banner</a>.
              <span class="changed">[CHANGED]</span>
            </p>

            <p class="changed">
              <span><a href="#nemelex_choice">NEMELEX' CHOICE</a></span> characters are now chosen by Nemelex from those with fewer than eight online wins. (Used to be fewer than six online wins)
              <span class="changed">[CHANGED]</span>
            </p>

            <p class="changed">
              <span>Yredelemnul</span> now requires three more distinct uniques to be killed to earn each tier of the <span><a href="#the_harvest">HARVEST</a></span> banner.
              <span class="changed">[CHANGED]</span>
            </p>
	    
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
              <span>|amethyst</span> for hosting the tournament scripts on CSZO.
            </p>
            <p>
              <span>Wensley</span>, <span>ChrisOelmueller</span>, and <span>Grunt</span> for creating the banner images.
            </p>
          </div>

        </div> <!-- Content -->
      </div>
    </div>
  </body>
</html>
