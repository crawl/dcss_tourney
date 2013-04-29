<%
   import query, loaddb, html, time, nemelex
   c = attributes['cursor']

   version = loaddb.T_VERSION
   year = loaddb.T_YEAR
   title = "Crawl %s Tournament Leaderboard" % version
   top_scores = query.find_games(c, sort_max='score', limit=3)

   nem_list = nemelex.list_nemelex_choices(c)

   if nem_list:
     pnem_list = []
     for x in nem_list[:-1]:
       if x[2] >= 5:
         pnem_list.append('<s>' + x[0] + ('(%d won)' % x[2]) + '</s>')
       else:
         pnem_list.append(x[0] + ('(%d won)' % x[2]))

   recent_wins = query.get_winning_games(c, limit = 5)
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
            Tournament starts on <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20130511T00">May 11, ${year} at 0:00 UTC (midnight May 11)</a>, and ends on
            <a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20130527T00">May 26, ${year} at 24:00 UTC (midnight May 27)</a>.
          </p>
        </div>
        <hr>

        <div class="content">

          % if nem_list:
          <div class="row nemelex">
            <table class="grouping" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <h3>Nemelex' Choice: </h3>
                  <span>${nem_list[-1][0]}</span>, chosen on ${nem_list[-1][1]} UTC
                  <p class="fineprint">
                    75 bonus points for the first five players to win ${nem_list[-1][0]}
                    during the tournament!
                  </p>

                  % if pnem_list:
                  <h3>Nemelex' Previous Choices: </h3>
                  ${", ".join(['<span>' + x + '</span>' for x in pnem_list])}
                  <p class="fineprint">
                    All previous Nemelex' Choices also remain valid during the
                    tournament until won by five players.
                  </p>
                  % endif
                </td>

                <td>
                  ${html.banner_named('nemelex', 3)}
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

          % if recent_wins:
          <div class="row">
          <div>
            <h3>Recent Wins</h3>
            ${html.games_table(recent_wins)}
          </div>

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
                Note: the abyssal and slimy runes are not eligible.
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
	            <h3>Most Uniques Killed: Clan</h3>
                    ${html.clan_unique_kills(c)}
                  </div>
	        </td>
                
                <td>
                  <div>
	            <h3>Most High Scores: Clan</h3>
                    ${html.clan_combo_highscores(c)}
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
