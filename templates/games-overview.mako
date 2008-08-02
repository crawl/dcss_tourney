<%

   import loaddb, query, crawl_utils, html
   c = attributes['cursor']

   all = query.get_all_game_stats(c)

%>

<div class="game_overview">
  <h2>Summary</h2>
  <table class="bordered">
    <tr>
      <th>Games Played</th> <th>Games Won</th> <th>Win %</th>
    </tr>
    <tr>
      <td class="numeric">${all['played']}</td>
      <td class="numeric">${all['won']}</td>
      <td class="numeric">${all['win_perc']}</td>
    </tr>
  </table>
</div>
