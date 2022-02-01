<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query
  import crawl_utils
  from crawl_utils import XXX_TOURNEY_BASE, base_link, player_link

  active_menu_item = "Clans"

  def linkify_player(name):
    return """<a href="{link}">{name}</a>""".format(
      link=player_link(name),
      name=name,
    )

  def points_for_result(result, category):
    if not result.rank:
      return 0
    if category.order_asc:
      return int(round((scoring_data.MAX_CATEGORY_SCORE * result.best) /
                       result.rank, 0))
    else:
      return int(round((scoring_data.MAX_CATEGORY_SCORE * result.rank) /
                       result.best, 0))

  def rank_for_result(result, category):
    if category.proportional:
      return str("%d/%d" % (result.rank, category.max))
    elif category.transform_fn is not None:
      return category.transform_fn(result.rank)
    else:
      return "{:,}".format(result.rank)
%>

<%block name="title">
  ${clan_name}
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1 class="display-4">${clan_name}</h1>
      <p class="lead">
        <b>
          Captain:
        </b>
        ${linkify_player(captain)}
      </p>
      <p class="lead">
        <b>
          Clan Members:
        </b>
        ${html.english_join([linkify_player(member) for member in clan_members if member != captain])}
      </p>
      <p class="lead">
        <b>
          Overall rank:
        </b>
        <a href="${XXX_TOURNEY_BASE}/teams.html">
          ${overall_rank}
          <small>
          of ${total_number_of_clans}
          </small>
        </a>
      </p>

    <%
    whereis = html.whereis(cursor, *clan_members)
    %>
    % if len(whereis) > 0:
    <div class="row">
      <div class="col">
        <p class="lead"><b>Ongoing Games:</b></p>
        <p>${whereis}</p>
      </div>
    </div>
    <hr>
    % endif

      <p class="lead">Recent games</p>

      ${html.full_games_table(
          query.find_games(cursor, player = clan_members, sort_max = 'end_time', limit = 10),
          count=False, win=False, caption="Recent games for %s" % clan_name,
          excluding=("race", "class", "title", "turns", "duration", "runes", "turns"),
          including=[[0, ('player', 'Player')], [2, ('charabbrev', 'Char')], [9, ('src', 'Server')]]
      )}

      <%
        clan_wins = query.find_games(cursor, player=clan_members, sort_max='score', killertype='winning', limit=None)
        # always show 5 top games, up to 10 if there are no wins
        top_game_count = max(5, 10 - len(clan_wins))
        best_games = query.find_games(cursor, player=clan_members, sort_max='score', killertype=('not', 'winning'), limit=top_game_count)
        top_game_header = "Top games" if len(clan_wins) == 0 else "Wins and top games"
      %>

      <p class="lead">${top_game_header}</p>

      ${html.full_games_table(
          clan_wins + best_games,
          count=False, win=False, caption=top_game_header + " for %s" % clan_name,
          excluding=("race", "class", "title", "turns", "duration", "runes", "turns"),
          including=[[0, ('player', 'Player')], [2, ('charabbrev', 'Char')], [9, ('src', 'Server')]]
      )}


      <h2>Categories</h2>
      <table class="table table-borderless table-dark table-striped table-hover w-auto">
        <thead>
          <tr>
            <th scope="col">Category</th>
            <th scope="col">Rank</th>
            <th scope="col">Points</th>
            <!--<th scope="col">Notes</th>-->
          <tr>
        </thead>
        <tbody>
          ## First row shows total score
          <tr class="table-secondary">
            <th scope="row">
              <a href="${base_link('teams.html')}">
                Total
              </a>
            </th>
            <th scope="row" class="text-monospace text-right">${overall_rank}</th>
            <th scope="row" class="text-monospace text-right">
              <%
                points = int(round(sum(float(points_for_result(clan_category_results[c.name], c) or 0.0) for c in scoring_data.CLAN_CATEGORIES), 0))
              %>
              ${'{:,}'.format(points)}
            </th>
            <!--<th scope="row"></th>-->
          </tr>

          % for category in scoring_data.CLAN_CATEGORIES:
          <%
            results = clan_category_results[category.name]
          %>
            <tr>
              <td>
                <a href="${base_link('clan-' + crawl_utils.slugify(category.name))}.html">
                  ${category.name}
                </a>
              </td>
              <td class="text-monospace text-right">${rank_for_result(results,
              category) if results.rank else '-'}</td>
              <td class="text-monospace
              text-right">${'{:,}'.format(points_for_result(results, category)) if results.rank else '-'}</td>
              <!--<td>${results.details if results.details else ''}</td>-->
            </tr>
          % endfor
        </tbody>
      </table>
    </div>
  </div>
</%block>
