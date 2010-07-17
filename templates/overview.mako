<%
   import query, loaddb, html, time, nemchoice
   c = attributes['cursor']

   title = "Crawl Tournament Leaderboard 2009"
   top_scores = query.find_games(c, sort_max='score', limit=3)

   in_sprint_window = loaddb.in_sprint_window()

   cnemelex = nemchoice.current_nemelex_choice()
   pnemelex = nemchoice.previous_nemelex_choices()

   recent_wins = query.get_winning_games(limit = 5)
   recent_sprint_wins = query.get_winning_games(limit = 5, sprint = True)
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>${title}</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>
  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>
      <div class="page_content">
        <div class="heading">
          <h1>${title}</h1>
          <p class="fineprint">
            Tournament starts Aug 1, 2009 at midnight UTC, and ends on
            Sep 1, 2009 at midnight UTC.
          </p>
        </div>
        <hr>

        <div class="content">

          % if cnemelex:
          <div class="row nemelex">
            <table class="grouping" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <h3>Nemelex' Choice: </h3>
                  <span>${cnemelex[0]}</span>, chosen on ${cnemelex[1]} UTC
                  <p class="fineprint">
                    100 bonus points for any player winning ${cnemelex[0]}
                    during the tournament! Only your first
                    winning ${cnemelex[0]} counts.
                  </p>

                  % if pnemelex:
                  <h3>Nemelex' Previous Choices: </h3>
                  ${", ".join(['<span>' + x + '</span>' for x in pnemelex])}
                  <p class="fineprint">
                    All previous Nemelex' Choices also remain valid during the
                    tournament.
                  </p>
                  % endif
                </td>

                <td>
                  ${html.banner_named('nemelex_choice')}
                </td>
              </tr>
            </table>
          </div>

          <hr>
          % endif

          <div class="row">
	        <table class="grouping" cellpadding="0" cellspacing="0">
	          <tr>
                <!-- Column one -->
                <td>
                  <div>
                    <h3>Leading Players</h3>
	                <%include file="overall-scores.mako"/>
                  </div>
	            </td>

                <!-- Column two -->
	            <td>
                  <div>
	                <h3>Leading Clans</h3>
                    ${html.best_clans(c)}
                  </div>
	            </td>
       	      </tr>
	        </table>
          </div>

          <hr>

          <div class="row">
            <div>
              <h3>Fastest Win (Turn Count)</h3>
              <%include file="fastest-turn.mako"/>
            </div>
            <div>
              <h3>Fastest Win (Real Time)</h3>
              <%include file="fastest-time.mako"/>
            </div>

            <div>
              <h3>Top Scores</h3>
              ${html.games_table(top_scores)}
            </div>
          </div>

          <hr>

          <div class="row">
            <div>
              <h3>First Victory</h3>
              <%include file="first-victory.mako"/>
            </div>
            <div>
	      <h3>First All-Rune Wins</h3>
	      <%include file="first-allrune.mako"/>
            </div>

            % if in_sprint_window:
            <div>
              <h3>First Sprint Victory</h3>
              <%include file="first-sprint-victory.mako"/>
            </div>
            % endif

          </div>

          <hr>

          <div class="row">
            <div>
	      <h3>Longest Streak</h3>
              ${html.best_streaks(c)}
            </div>

            <div>
              <h3>Active Streaks</h3>
              ${html.best_active_streaks(c)}
            </div>
          </div>

          <hr>

          % if recent_wins or recent_sprint_wins:
          <div class="row">
            % if recent_wins:
            <div>
              <h3>Recent Wins</h3>
              ${html.games_table(recent_wins)}
            </div>
            % endif

            % if recent_sprint_wins:
            <div>
              <h3>Recent Sprint Wins</h3>
              ${html.games_table(recent_sprint_wins)}
            </div>
            % endif
          </div>
          <hr>
          % endif

          <div class="row">
            <table class="grouping" cellspacing="0" cellpadding="0">
              <tr>
                <td>
                  <div>
                    <h3>Most High Scores</h3>
                    ${html.combo_highscorers(c)}
                  </div>
                </td>
                <td>
                  <div>
	                <h3>Most Uniques Killed</h3>
                    <%include file="most-uniques-killed.mako"/>
                  </div>
                </td>
              </tr>
            </table>
          </div>

          <hr>

          <div class="row">
            <div>
              <h3>Ziggurat Raiders</h3>
              ${html.best_ziggurats(c)}
            </div>

            <div>
              <h3>Runes Fetched at Lowest XL</h3>
              ${html.youngest_rune_finds(c)}
              <p class="fineprint">
                Note: the abyssal rune is not eligible.
              </p>
            </div>

            <div>
              <h3>Most Pacific Wins</h3>
              ${html.most_pacific_wins(c)}
              <p class="fineprint">
                Winning games with the fewest slain creatures.
              </p>
            </div>

            <div>
              <h3>Most Deaths to Uniques</h3>
              ${html.most_deaths_to_uniques(c)}
            </div>
          </div>

          <hr>

          <div class="row">
	    <table class="grouping" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <div>
	            <h3>Most High Scores: Clan</h3>
                    ${html.clan_combo_highscores(c)}
                  </div>
	        </td>

	        <td>
                  <div>
	            <h3>Most Uniques Killed: Clan</h3>
                    ${html.clan_unique_kills(c)}
                  </div>
	        </td>
              </tr>
            </table>
          </div>
        </div> <!-- Content -->
      </div>
    </div>
    ${html.update_time()}
  </body>
</html>
