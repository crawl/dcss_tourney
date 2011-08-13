<%
   import loaddb
   version = loaddb.T_VERSION
   year    = loaddb.T_YEAR
   title   = "Crawl %s Tournament Information" % year
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
      <%include file="toplink.mako"/> 

      <div class="page_content">
        <div class="heading">
          <h1>${title}</h1>
          <p class="fineprint">
            Tournament starts Aug 13, ${year} at midnight UTC, and ends on
            Aug 29, ${year} at midnight UTC.
          </p>
        </div>
        <hr>

        <div class="content">
          <p>
            Hello all! Welcome to the rules for the crawl.akrasiac.org
            ${year} Dungeon Crawl Stone Soup Tournament. The simple part:
            Play on <a href="http://crawl.akrasiac.org">crawl.akrasiac.org</a>
            or <a href="http://crawl.develz.org">crawl.develz.org</a> and all of
            your Crawl ${version} games that <b>start after midnight UTC on
            August 13</b> and <b>end before midnight UTC on August 29</b> will
            count toward the tournament.
          </p>

          <div class="inset">
            <p>
              <span class="inline_heading">Important note to those playing on CDO:</span> For
              the first few days of the tournament, you might not see
              any mention of version 0.9 on the crawl.develz.org server.
              If so, then the option "T) Go to Dungeon Crawl Stone Soup Trunk"
              really is 0.9 and games played in that version will count
              for the tournament.
            </p>
            <p>
              Also, webtiles on crawl.develz.org will unfortunately not be updated
              to 0.9 until a few days after the tournament begins, and it will not
              be possible to compete in the tournament using webtiles until then.
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
            need to add a line to the top of your <b>CAO ${version}</b> rcfile
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
            other team members in her <b>CAO ${version}</b> rcfile, like this:
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
              <span class="inline_heading">For emphasis:</span> clan membership lines should be added to
              your crawl.akrasiac.org ${version} rcfile. Even if you're playing
              your games on crawl.develz.org, you must add clan
              membership information to your crawl.akrasiac.org
              ${version} rcfile.
            </p>
          </div>

          <p>
            Clan names must contain only alphanumeric characters,
            underscores, and hyphens. Once a player's username is in
            the captain's rcfile and the captain's username is in the
            player's rcfile and our script checks for updates, the
            players will be in the same clan.
          </p>

          <p>
            Clans may be changed by adding or removing players at any
            time until midnight UTC on <b>Aug 21</b>, after which clans will be
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
              <span>50 points</span> for a player's second win that is
              not a repeat race or class of the character from her
              first win.
            </p>

            <p>
              <span>10 points</span> for each win of a player after
              her first win (unless this is the second win and earned
              50 points from the rule above).
            </p>

            <p>
              <span>25 extra points</span> for each win by a player
              with a god (including "No God") that the player did not
              previously win a game in the tournament with. For purposes of
              these points we say that a player wins with a god if she reaches
              full (******) piety with that god before reaching full piety with
              any other god. For Xom, you must play a Chaos Knight and never
              abandon Xom.
            </p>

            <p>
              <span>50 extra points</span> for each consecutive (streak) win
              by a player with a race that has not 
	      previously been a streak win for that player.
            </p>
            <p>
              <span>25 extra points</span> for each consecutive (streak) win
              by a player with a class that has not 
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
            <h2>RACE AND CLASS WINS</h2>
            <p>
              <span>2*(48+T)/(2+R) points</span> (rounded up) for a win with a given race if T is the total number of games won in the tournament before the start of the win in question and R of those T were with the given race. If a player wins the same race multiple times, she only gets the largest value of this bonus among the wins, not the sum.

              For example, if there have been 10 games won prior to the start of the win in question and 2 of them were with the same race, then the
              win will be worth 2*(48+10)/(2+2) = 29 additional points.
            </p>
            <p>
              <span>(54+T)/(2+C) points</span> (rounded up) for a win with a given class if T is the total number of games won in the tournament before the start of the win in question and C of those T were with the given class. If a player wins the same class multiple times, she only gets the largest value of this bonus, not the sum.
            </p>
            <div class="inset">
              <p>
	        For clan scoring, if a clan has multiple wins for the same race
                or class, only the largest value of the bonus among the wins
                is used, not the sum.
	      </p>
            </div>
            <div class="inset">
              <p>
	        The current values of the bonus for each race and class will be
                listed on the "Species/Classes" page for your convenience.
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
	      a streak is defined as min(number of distinct races used, number 
	      of distinct classes used).
              Ties are broken by the first to achieve the streak.
            </p>
            <p>
              <span>100 bonus points</span> for the win with the last
              starting time (among tournament wins) in the tournament.
            </p>
	    <p>
	      <span>40 bonus points</span> for a win without visiting
	      Temple, Lair, Orc, Hive, or the Vaults (<a href="#lord_of_darkness">LORD OF DARKNESS</a> banner).
	    </p>
            <p>
              <span>75 bonus points</span> for winning <a href="#nemelex_choice">NEMELEX' CHOICE</a> characters. The first Nemelex' Choice combo is chosen at the start of the tournament, and after that each one is chosen when the previous one is won for the first time. Each combo remains valid until it has been won five times. The race/class combinations are chosen by Nemelex from those with the fewest wins in Crawl version 0.6 and newer, with no race or class repeated.
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
              <span>5 points</span> per high score in a race/class combination
              (HuWn, not just Hu).
            </p>

            <p>
              <span>5 additional points</span> for each high score in a
              race/class combination that is attained by a win.
            </p>

            <p><span>20 points</span> per high score in a race.</p>

            <p><span>10 points</span> per high score in a class.</p>

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
            <h2>CLAN POINTS ONLY</h2>

            <p>
              These get you clan points but do not get you points
              toward the individual prize, encouraging
              specialization within clans but making the hypothetical
              "Best Crawl Player" award based on more "real"
              metrics.
            </p>

            <p>
              <span>200-100-50 clan points</span> for deepest level reached
              in a Ziggurat. Completing a Ziggurat level (for instance
              exiting to the dungeon from Zig:20) is also noted and is
              better than merely reaching the level. Ties are broken by who 
	      reaches/exits the Ziggurat level first.
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
	      scores in race/class combinations.
            </p>

            <p>
              <span>200-100-50 clan points</span> for the <b>clans</b> with the most
              high scores in race/class combos.
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
              "Race and class wins" points (which are computed on 
              the level of clans as described in that section), plus the 
	      "Clan points only" trophies above.
            </p>

            <p>
              Six players or fewer per clan.
            </p>
          </div>

          <div class="banner-desc">
            <h2>BANNERS</h2>

            <hr>

            <div>
	      <img src="images/banner_ashenzari.png"
                   alt="Runic Literacy"
                   title="Runic Literacy"
                   width="150" height="55"
                   >
              <p>
                Ashenzari thinks that runes are really interesting and wants
                players to achieve 
                <a name="runic_literacy">RUNIC LITERACY</a>, finding each
                rune sometime during the tournament.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_beogh.png"
                   alt="Saint"
                   title="Saint"
                   width="150" height="55"
                   >
              <p>
	        Beogh thinks that the only thing more important than
                having friends is dominating your friends, and will recognize
                as a <a name="saint">SAINT</a> the player with the highest
                tournament score (100 points minimum) on each clan.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_cheibriados.png"
                   alt="Slow and Steady"
                   title="Slow and Steady"
                   width="150" height="55"
                   >
              <p>
                Cheibriados believes in being
                <a name="slow_and_steady">SLOW AND STEADY</a> and will
                so recognize players who are careful enough to win two
                games in a row.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_elyvilon.png"
                   alt="The Pantheon"
                   title="The Pantheon"
                   width="150" height="55"
                   >
              <p>
                Elyvilon thinks it's important to check out what all
                the gods have to offer and thus will
                give <a name="the_pantheon">THE PANTHEON</a> to any
                player who becomes the Champion (******) of every god
                (other than Xom) over
                the course of the tournament.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_fedhas.png"
                   alt="The Fruit Basket"
                   title="The Fruit Basket"
                   width="150" height="55"
                   >
              <p>
                Fedhas is extraordinarily fond of fruit and
                vegetables, and will award <a name="the_fruit_basket">THE
                FRUIT BASKET</a> to a player who finds every kind of
                fruit (pear, apple, choko, apricot, orange, banana,
                strawberry, rambutan, lemon, grape, sultana, lychee, snozzcumber)
                over the course of the tournament. Fruits count toward
                the Fruit Basket when picked up - merely finding the fruit
                on the ground or eating it off the ground does not.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_jiyva.png"
                   alt="Gelatinous Body"
                   title="Gelatinous Body"
                   width="150" height="55"
                   >
              <p>
                Jiyva thinks that it is important to be flexible and will gift
                players who reach experience level 9 with at least 9 distinct
                races and at least 9 distinct classes with a 
                <a name="gelatinous_body">GELATINOUS BODY</a>.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_kikubaaqudgha.png"
                   alt="Lord of Darkness"
                   title="Lord of Darkness"
                   width="150" height="55"
                   >
              <p>
                Kikubaaqudgha wants players to demonstrate their mastery over
                the forces of darkness without delay, and will recognise any
                player who wins without wasting time entering any branch as
                a <a name="lord_of_darkness">LORD OF DARKNESS</a>. (<span>+40
                points</span> for each game won without entering Temple, Lair,
                Orc, Hive, or the Vaults.)
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_lugonu.png"
                   alt="The Atheist"
                   title="The Atheist"
                   width="150" height="55"
                   >
              <p>
                Lugonu, who hates the other gods, would like to
                award <a name="the_atheist">THE ATHEIST</a> to any winning
                player who never worshipped a god even though having the option
                of doing so (not a demigod).
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_makhleb.png"
                   alt="Speed Demon"
                   title="Speed Demon"
                   width="150" height="55"
                   >
              <p>
                Makhleb wants to see bloodshed as quickly as possible and
                will recognise any player who reaches D:27 in no more than 27
                minutes as a true <a name="speed_demon">SPEED DEMON</a>.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_nemelex.png"
                   alt="Nemelex' Choice"
                   title="Nemelex' Choice"
                   width="150" height="55"
                   >
              <p>
                Nemelex Xobeh wants to see players struggle and loves
                randomness, and so will give the
                <a name="nemelex_choice">NEMELEX' CHOICE</a> award
                to the first five players to win each of several combos
                randomly chosen and announced throughout the
                tournament.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_okawaru.png"
                   alt="The Orb"
                   title="The Orb"
                   width="150" height="55"
                   >
              <p>
                Okawaru is all about winning, all the time, and thus
                will award <a name="the_orb">THE ORB</a> to any player who
                successfully wins.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_sif.png"
                   alt="The Scholar"
                   title="The Scholar"
                   width="150" height="55"
                   >
              <p>
                Sif Muna thinks that a broad base of knowledge is important
                and will award <a name="the_scholar">THE SCHOLAR</a>
                to any player who raises every magic skill to 15 over the
                course of the tournament.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_tso.png"
                   alt="Discovered Language"
                   title="Discovered Language"
                   width="150" height="55"
                   >
              <p>
                The Shining One thinks it's about time that the player
                <a name="discovered_language">DISCOVERED LANGUAGE</a> by
                finding her first rune.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_trog.png"
                   alt="The Scythe"
                   title="The Scythe"
                   width="150" height="55"
                   >
              <p>
                Trog, who hates spellcasters, would like to
                award <a name="the_scythe">THE SCYTHE</a> to any player
                who kills Sigmund in the Temple before reaching experience
                level 10.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_vehumet.png"
                   alt="Let it end in hellfire"
                   title="Let it end in hellfire"
                   width="150" height="55"
                   >
              <p>
                Vehumet wants you to
                <a name="let_it_end_in_hellfire">LET IT END IN HELLFIRE</a> and
                thus encourages you to enter
                one of Swamp, Snake, Shoals, Slime, Vaults, and Tomb for the
                first time and get the rune there... all after having
                picked up the Orb of Zot.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_xom.png"
                   alt="Descent into Madness"
                   title="Descent into Madness"
                   width="150" height="55"
                   >
              <p>
                Xom is always looking for entertainment and thinks it would be
                hilarious to watch a player's
                <a name="descent_into_madness">DESCENT INTO MADNESS</a>
                through 27 ziggurat levels
                (possibly over multiple games and multiple ziggurats).
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_yredelemnul.png"
                   alt="The Harvest"
                   title="The Harvest"
                   width="150" height="55"
                   >
              <p>
                Yredelemnul demands that clans attempt to kill every unique and
                will recognise success by awarding 
                <a name="the_harvest">THE HARVEST</a> to each member of such
                a clan.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_zin.png"
                   alt="Angel of Justice"
                   title="Angel of Justice"
                   width="150" height="55"
                   >
              <p>
                Zin will give the
                <a name="angel_of_justice">ANGEL OF JUSTICE</a> award to any
                player who cleanses Hell and Pandemonium by killing all the
                demon lords who reside there (Antaeus, Asmodeus, Cerebov,
                Dispater, Ereshkigal, Gloorx Vloq, Lom Lobon, and Mnoleg)
                over the course of the tournament.
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
                Some rules have been changed from the 2010
                tournament. This is a list of rules differences. Changes that
                were already adopted in the unofficial 0.8 tournament in May
                2011 are listed here as well.
              </p>

              <p><span class="removed">[REMOVED]</span>
                flags rules that existed in 2010 and are gone in
                this tournament.</p>

              <p><span class="added">[NEW]</span>
                flags rules that are new to this tournament</p>

              <p><span class="changed">[CHANGED]</span>
                flags rules that have been modified for this 
		tournament. To compare
                changed rules with the rules for 2010, see
                the <a href="http://crawl.akrasiac.org/tourney10">2010
                rules</a>
              </p>
            </div>

            <hr>

            <p class="added">
              <span>2*(48+T)/(2+R) points</span> (rounded up) for a win with a given race if T is the total number of games won in the tournament before the start of the win in question and R of those T were with the given race. If a player wins the same race multiple times, she only gets the largest value of this bonus among the wins, not the sum (and the same for clans).
              <span class="added">[NEW]</span>
            </p>
            <p class="added">
              <span>(54+T)/(2+C) points</span> (rounded up) for a win with a given class if T is the total number of games won in the tournament before the start of the win in question and C of those T were with the given class. If a player wins the same class multiple times, she only gets the largest value of this bonus, not the sum (and the same for clans).
              <span class="added">[NEW]</span>
            </p>
            <p class="changed">
	      <span>5,000,000/turncount points</span> for each player's fastest win (by turncount). (Previously 200-100-50 points for the fastest three games.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>1,250,000/duration points</span> for each player's fastest win (by realtime, measured in seconds). (Previously 200-100-50 points for the fastest three games.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>score/120,000 points</span> for each player's highest scoring winning game. (Previously 200-100-50 points for the highest scoring three games.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
              <span>50 extra points</span> for each consecutive (streak) win
              by a player with a race that has not 
	      previously been a streak win for that player. (Previously streak points were computed differently.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>25 extra points</span> for each consecutive (streak) win
              by a player with a class that has not 
	      previously been a streak win for that player. (Previously streak points were computed differently.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>200-100-50 points</span> for longest streak of
              winning games, where "length" of 
	      a streak is defined as min(number of distinct races used, number 
	      of distinct classes used). (Previously diversity of the streak 
	      did not matter here.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
              <span>25 extra points</span> for each win by a player
              with a god (including "No God") that the player did not
              previously win a game in the tournament with. For purposes of
              these points we say that a player wins with a god if she reaches
              full (******) piety with that god before reaching full piety with
              any other god. For Xom, you must never have worshipped another god.
              (Was 20 points, full piety was not required,
              changing gods was not allowed.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
              <span>30/N points</span> (rounded up) each time you find a 
              type of rune for the Nth time. (Was 50 points for the first 
	      time and 1 point each time after the first.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
              <span>20 points</span> per high score in a race. (Was 10 points.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>200-100-50 clan points</span> for the players with the most high scores in race/class combinations. (Was individual points previously.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
              <span>40 bonus points</span> for a win without visiting Temple, Lair, Orc, Hive, or the Vaults (<a href="#lord_of_darkness">LORD OF DARKNESS</a> banner). (Was 20 bonus points and just not visiting Lair.)
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>75 bonus points</span> for winning <a href="#nemelex_choice">NEMELEX' CHOICE</a> characters. The first Nemelex' Choice combo is chosen at the start of the tournament, and after that each one is chosen when the previous one is won for the first time. Each combo remains valid until it has been won five times. The race/class combinations are chosen by Nemelex from those with the fewest wins in Crawl version 0.6 and newer, with no race or class repeated.
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="changed">
	      <span>Many other banners</span> were altered or replaced by new ones.
              <span class="changed">[CHANGED]</span>
            </p>
            <p class="removed">
              <span>50 extra points</span> for a player's first
              all-rune victory.
              <span class="removed">[REMOVED]</span>
            <p class="removed">
              <span>30 extra points</span> for each non-consecutive
              win by a player that is not a repeat race or class of
              any of her prior wins.
              <span class="removed">[REMOVED]</span>
            </p>
            <p class="removed">
              <span>10 extra points</span> for each non-consecutive
              win by a player that is a repeat race xor class of
              any of her prior wins.
              <span class="removed">[REMOVED]</span>
            </p>
            <p class="removed">
	      <span>100 points</span> for a player's first game where she 
	      destroys the Orb of Zot.
              <span class="removed">[REMOVED]</span>
            </p>
	    <p class="removed">
	      <span>200-100-50 clan points</span> for fewest creatures
              killed (including by summons, &amp;c.) in a win.
              <span class="removed">[REMOVED]</span>
            </p>
	    <p class="removed">
	      <span>10 clan points</span> for each distinct skill raised to
              level 27.
              <span class="removed">[REMOVED]</span>
            </p>
	    <p class="removed">
	      <span>All points</span> for Sprint games.
              <span class="removed">[REMOVED]</span>
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
            <p>
            <p>
              <span>Wensley</span> for the new banner images.
            </p>
              <span>Onia</span>, <span>due</span>, and <span>purge</span> for
              the old banner images.
            </p>
          </div>

        </div> <!-- Content -->
      </div>
    </div>
  </body>
</html>
