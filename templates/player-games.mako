<%
  import html
  import scoring_data
  import query
%>

  <div class="row">
    <div class="col">
      <h2>Recent Games</h2>
      ${html.full_games_table(
          query.find_games(cursor, player = player, sort_max = 'end_time', limit = 10),
          count=False, win=False, caption="Recent games for %s" % player,
          excluding=("race", "class", "title", "turns", "duration", "runes", "turns"),
          including=[[1, ('charabbrev', 'Char')], [8, ('src', 'Server')]]
        )}
    </div>
  </div>
  <div class="row">
    <div class="col">
      <h2>Won Games</h2>
      ${html.ext_games_table(query.get_winning_games(cursor, player = player),
         caption="Recent wins for %s" % player,
          excluding=("race", "class", "title", "turns", "duration", "runes", "turns"),
          including=[[1, ('charabbrev', 'Char')], [8, ('src', 'Server')]]
        )}
    </div>
  </div>

