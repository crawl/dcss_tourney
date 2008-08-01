<%
   import loaddb, query
   c = attributes['cursor']
%>

<table>
  <tr>
    <th></th> <th>Player</th> <th>Points</th>
  </tr>

  <%
  top_players = query.get_top_players(c)
  count = 0
  %>

  % for player, points in top_players:
  <% count += 1 %>
  <tr>
    <td>${count}</td>
    <td>${player}</td>
    <td class="numeric">${str(points)}</td>
  </tr>
  % endfor
</table>
