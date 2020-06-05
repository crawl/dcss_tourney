<%inherit file="base.mako"/>

<%!
  import query

  active_menu_item="Search"
%>

<%block name="title">
  Search for players and teams
</%block>

<%block name="main">
  <%
    c = attributes['cursor']
    players = query.get_all_players(c)
    clans = query.get_all_clans(c)
  %>

  <div class="lr-flex">
      <div>
          <input type="text" id="player-search" oninput="player_search_update(false)" placeholder="Search for players by name">
          <div id="player-search-div">
            <ul class="search-list">
              %for p in players:
                <li>${p[1]}</li>
              %endfor
            </ul>
          </div>
      </div>
      <div>
          <input type="text" id="clan-search" oninput="clan_search_update(false)" placeholder="Search for clans by name">
          <div id="clan-search-div">
            <ul class="search-list">
            %for c in clans:
              <li>${c[2]}</li>
            %endfor
            </ul>
          </div>
      </div>
  </div>
</%block>
