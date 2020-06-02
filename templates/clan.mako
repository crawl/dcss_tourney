<%inherit file="base.mako"/>

<%!
  import scoring_data
  import html
  import query
  from crawl_utils import XXX_TOURNEY_BASE

  active_menu_item = "Clans"

  def pretty_clan_name(name):
    return name.replace('_', ' ')

  def linkify_player(name):
    return """<a href="{XXX_TOURNEY_BASE}/players/{name}.html">{name}</a>""".format(
      XXX_TOURNEY_BASE=XXX_TOURNEY_BASE,
      name=name
    )
%>

<%block name="title">
  ${pretty_clan_name(clan_name)}
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1>${pretty_clan_name(clan_name)}</h1>
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
          count=False, win=False, caption="Recent games for %s" % pretty_clan_name(clan_name),
          excluding=("race", "class", "title", "turns", "duration", "runes", "turns"),
          including=[[0, ('player', 'Player')], [2, ('charabbrev', 'Char')], [9, ('src', 'Server')]]
      )}
    </div>
  </div>
</%block>
