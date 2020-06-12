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

  def points_for_rank(rank_num):
    if not rank_num:
      return "-"
    return str(int(round(scoring_data.MAX_CATEGORY_SCORE / rank_num, 0)))
%>

<%block name="title">
  ${clan_name}
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1>${clan_name}</h1>
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
      ${html.full_games_table(
          query.find_games(cursor, player = clan_members, sort_max = 'end_time', limit = 10),
          count=False, win=False, caption="Recent games for %s" % clan_name,
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
              points = int(
                round(
                  sum(
                    float(points_for_rank(result.rank))
                    for result in clan_category_results.values()
                    if result.rank is not None
                  ) / len(clan_category_results)
                , 0)
              )
              %>
              ${'{:,}'.format(points)}
            </th>
            <th scope="row"></th>
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
              <td class="text-monospace text-right">${results.rank if results.rank else '-'}</td>
              <td class="text-monospace text-right">${'{:,}'.format(int(points_for_rank(results.rank))) if results.rank else '-'}</td>
              <!--<td>${results.details if results.details else ''}</td>-->
            </tr>
          % endfor
        </tbody>
      </table>
    </div>
  </div>
</%block>
