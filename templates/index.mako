<%
   import loaddb
   version = loaddb.T_VERSION
   year    = loaddb.T_YEAR
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
      <%include file="toplink.mako"/> 

      <div class="page_content">
        <div class="heading">
          <h1>${title}</h1>
          <p class="fineprint">
            Tournament starts May 14, ${year} at midnight UTC, and ends on
            May 30, ${year} at midnight UTC.
          </p>
        </div>
        <hr>

        <div class="content">
          <p>
            Hello all! Welcome to the rules for the
            ${version} Dungeon Crawl Stone Soup Tournament. The simple part:
            Play on <a href="http://crawl.akrasiac.org">crawl.akrasiac.org</a>
            or <a href="http://crawl.develz.org">crawl.develz.org</a> and all of
            your Crawl ${version} games that <b>start after midnight UTC on
            May 14</b> will count toward the tournament.
          </p>

          <p>
            For players who participated in previous
            tournaments, please look at
            the <a href="#changes">Changes</a> section for a list of
            rule changes from last year.
          </p>

          <p>
            This tournament is unofficial and is not intended to replace
 	    the usual August tournament. 
	    The idea for this tournament is simply to celebrate the release of
	    0.8 and have fun playing Crawl.
          </p>

          <p>
            Participants in the tournament may form clans of six or
            fewer players. If you wish to be a member of a clan, you
            need to add a line to the top of your <b>CAO 0.8</b> rcfile like
            this:
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
            other team members in her <b>CAO 0.8</b> rcfile, like this:
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
              your crawl.akrasiac.org 0.8 rcfile. Even if you're playing
              your games on crawl.develz.org, you must add clan
              membership information to your crawl.akrasiac.org
              0.8 rcfile.
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
            time until midnight UTC on May 22, after which clans will be
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
              <span>50 extra points</span> for a player's first
              all-rune victory.
            </p>

            <p>
              <span>20 extra points</span> for each win by a player
              with a god (including "No God") that the player did not
              previously win a game in the tournament with. This does
              not apply if you changed gods during the game.
            </p>

            <p>
              <span>40 extra points</span> for each consecutive (streak) win
              by a player with a race/class combination that has not 
	      previously been a streak win for that player. Such a game does 
	      not have to be of a new race 
              or class, but note that to be eligible for the "longest streak" 
              award below all games must have distinct races and classes.
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
              <span>2*N extra points</span> for each race, split evenly 
	      (rounding up) among 
              all players to win at least one game with that race, where N 
	      is the 
              total number of games won in the tournament. For example, if a 
	      total of 105 games are won during the tournament and 4 players 
	      won at least one ogre, then each of the 4 players is awarded 
	      53 extra points (2*105/4 = 52.5) for this.
            </p>

            <p>
              <span>N extra points</span> for each class, split evenly 
	      (rounding up) among 
              all players to win at least one game with that class, where N 
	      is the 
              total number of games won in the tournament.
            </p>
            <p>
              <span>50 extra points</span> for each race/class combination, 
	      split evenly (rounding up) among 
              all players to win at least one game with that race/class
	      combination. However, if only a single person wins a given 
	      race/class combination, then she will only be awarded 25 points 
	      rather than 50.
            </p>
            <div class="inset">
              <p>
	        For clan scoring, these points are instead split evenly among 
		all <b>clans</b> to win at least one game (counting 
		individuals without clans as 1-person clans).
	      </p>
            </div>
          </div>
          <hr>

          <div>
            <h2>SPECIAL WINS</h2>

            <p><span>200/100/50 points</span> for fastest win in realtime.</p>
            <p><span>100/50/20 points</span> for fastest 15-rune win
	      in realtime.</p>
            <p><span>200/100/50 points</span> for fastest win by turncount.</p>
            <p><span>200/100/50 points</span> for first win scored.</p>
            <p><span>200/100/50 points</span> for first 15-rune victory.</p>
            <p><span>200/100/50 points</span> for longest streak of
              winning games with distinct races and classes. 
              Ties are broken by the first to achieve the streak.
            </p>
            <p>
              <span>100 bonus points</span> for the win with the last
              starting time (among tournament wins) in the tournament.
            </p>
            <p>
              <span>20 bonus points</span> for a win without
              visiting the Lair.
            </p>
	    <p>
	      <span>20 bonus points</span> (in addition to the 20 for 
	      a Lairless win) for a win without visiting
	      Temple, Lair, Orc, Hive, or the Vaults.
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

            <p>
              <span>200/100/50 points</span> for the games with the highest
              scores overall.
            </p>

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

            <p>
              <span>200/100/50 points</span> for the players with the most high 
	      scores in race/class combinations.
            </p>

          </div>

          <hr>

          <div>
            <h2>UNIQUES</h2>

            <p><span>5 points</span> the first time you kill each
              unique.</p>

            <p><span>50/20/10 points</span> for the players with the most unique 
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
              <span>200/100/50 clan points</span> for deepest level reached
              in a Ziggurat. Completing a Ziggurat level (for instance
              exiting to the dungeon from Zig:20) is also noted and is
              better than merely reaching the level.
            </p>

            <p><span>50/20/10 clan points</span> for lowest XL at which a
            rune is picked up, not including the abyssal and slimy runes.</p>

            <p>
              <span>50/20/10 clan points</span> for the "Most Unique Deaths"
              trophy: Killed by the most unique uniques.
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
              <span>200/100/50 clan points</span> for the <b>clans</b> with the most
              high scores in race/class combos.
            </p>

            <p>
              <span>100/50/20 clan points</span> for the <b>clans</b> with the most
              unique uniques killed.
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
            <h2>PENNANTS</h2>

            <hr>

            <div>
	      <img src="images/banner_temple.png"
                   alt="temple"
                   title="Temple"
                   width="150" height="55"
                   >
              <p>
                Any player who aids the path of pilgrims to the Ecumenical Temple
		by killing the troublesome Sigmund will be granted the 
		Pennant of the <a name="temple">TEMPLE</a> in appreciation.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_orc.png"
                   alt="orc"
                   title="Orc"
                   width="150" height="55"
                   >
              <p>
	        Any player who obtains 1000 gold or more in a single game 
		will gain the (grudging) respect of the orcs and thus will be 
		granted the Pennant 
		of the <a name="orc">ORCISH MINES</a>. 
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_lair.png"
                   alt="lair"
                   title="Lair"
                   width="150" height="55"
                   >
              <p>
                The shallowest runes of Zot reside 
		in the Lair of Beasts and thus upon finding her very first rune
		a player will be granted the Pennant 
		of the <a name="lair">LAIR</a>.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_hive.png"
                   alt="hive"
                   title="Hive"
                   width="150" height="55"
                   >
              <p>
                Any player who spends at least 27 hours playing over the 
		course of the tournament (playing as busily as a bee, as it were) 
		will be granted 
		the Pennant of the <a name="hive">HIVE</a>.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_vaults.png"
                   alt="vaults"
                   title="Vaults"
                   width="150" height="55"
                   >
              <p>
                Any player who finds and enters every portal vault at least once over 
		the course of the tournament will be granted the Pennant of 
		the <a name="vaults">VAULTS</a>. (The portal vaults are Sewer,
		Ossuary, Bailey, Labyrinth, Bazaar, Volcano, Ice Cave, 
		Spider's Nest, Wizard Lab, and Treasure Trove.)
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_hell.png"
                   alt="hell"
                   title="Hell"
                   width="150" height="55"
                   >
              <p>
                Any player who kills all the lords of Hell and 
                Pandemonium (Antaeus, Asmodeus, Cerebov, Dispater, Ereshkigal, 
                Gloorx Vloq, Lom Lobon, and Mnoleg) over the course of the 
                tournament will be granted the Pennant 
		of <a name="hell">HELL</a>.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_pan.png"
                   alt="pan"
                   title="Pan"
                   width="150" height="55"
                   >
              <p>
                Any player who enters a ziggurat and manages to reach its tenth 
		level 
		will be granted the Pennant of <a name="pan">PANDEMONIUM</a>.
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_abyss.png"
                   alt="abyss"
                   title="Abyss"
                   width="150" height="55"
                   >
              <p>
                Any player who wins a "branchless" game will be granted the 
		Pennant of the <a name="abyss">ABYSS</a>. (A "branchless" 
		game is one in which one wins without ever entering Temple, Lair, 
		Orc, Hive, or the Vaults.)
              </p>
            </div>

	    <hr>

            <div>
	      <img src="images/banner_zot.png"
                   alt="zot"
                   title="Zot"
                   width="150" height="55"
                   >
              <p>
                Any player who successfully carries the Orb of Zot out of
		the dungeon will be granted the Pennant 
		of <a name="zot">ZOT</a>.
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
                tournament. This is a list of rules differences.
		Note that some rules that were removed for this tournament
		may be back in the August 2011 tournament.
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
              <span>2*N extra points</span> for each race, split evenly (rounding 
	      up) among 
              all players to win at least one game with that race, where N is the 
              total number of games won in the tournament. (Computed on a
	      per-clan basis for clan points.)
              <span class="added">[NEW]</span>
            </p>
            <p class="added">
              <span>N extra points</span> for each class, split evenly (rounding up)
	      among 
              all players to win at least one game with that class, where N is the 
              total number of games won in the tournament. (Done on a
	      per-clan basis for clan points.)
              <span class="added">[NEW]</span>
            </p>
            <p class="added">
              <span>50 extra points</span> for each race/class combination, 
	      split evenly (rounding up) among 
              all players to win at least one game with that race/class
	      combination. However, if only a single person wins a given 
	      race/class combination, then she will only be awarded 25 points 
	      rather than 50.
	      <span class="added">[NEW]</span>
            </p>
	    <p class="added">
	      <span>100/50/20 points</span> for fastest 15-rune win
	      in realtime.
	      <span class="added">[NEW]</span>
	    </p>
	    <p class="added">
	      <span>20 bonus points</span> (in addition to the 20 for 
	      a Lairless win) for a win without visiting
	      Temple, Lair, Orc, Hive, or the Vaults.
	    <span class="added">[NEW]</span>
            <p class="changed">
              <span>40 extra points</span> for each consecutive (streak) win
              by a player with a race/class combination that has not 
	      previously been a streak win for that player. (Was 100/30/10 
	      points depending on whether it was 
 	      a repeat race/class, with no restriction on streaking the same 
	      combo in multiple streaks.)
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
	    <p class="removed">
              <span>10 points</span> for each win of a player after
              her first win.
              <span class="removed">[REMOVED]</span>
            </p>
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
              <span>100 bonus points</span> for winning Nemelex'
              Choice characters.
              <span class="removed">[REMOVED]</span>
            </p>
            <p class="removed">
	      <span>100 points</span> for a player's first game where she 
	      destroys the Orb of Zot.
              <span class="removed">[REMOVED]</span>
            </p>
	    <p class="removed">
	      <span>200/100/50 clan points</span> for fewest creatures
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
	      scripts used in the August tournaments and modified for use in 
	      this tournament.
	    </p>
	    <p>
	      <span>rwbarton</span> for hosting the tournament pages 
	      and scripts.
	    </p>
            <p>
              <span>Wensley</span> for the new banner/pennant images.
            </p>
          </div>

        </div> <!-- Content -->
      </div>
    </div>
  </body>
</html>
