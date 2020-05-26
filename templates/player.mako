<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  from crawl_utils import XXX_TOURNEY_BASE
  import html
  import scoring_data
  import query

  # Set active top level menu item
  active_menu_item = 'Players'

  def rank_ordinal(num):
    if num == 0:
      return u'∞'
    remainder = num % 10
    suffix = 'th'
    if remainder == 1:
      suffix = 'st'
    elif remainder == 2:
      suffix = 'nd'
    elif remainder == 3:
      suffix = 'rd'
    if (num % 100) in (11, 12, 13):
      suffix = 'th'
    return '%s<sup>%s</sup>' % (num, suffix)

  def points_for_rank(rank_num):
    if not rank_num:
      return "-"
    return str(int(round(scoring_data.MAX_CATEGORY_SCORE / rank_num, 0)))

  def pretty_points(points):
    return '{:,}'.format(int(points))

  def rank_description(rank_num):
    if rank_num is None:
      return u"0 points <small>(rank: ∞)</small>"
    else:
      points = points_for_rank(rank_num)
      ordinal = rank_ordinal(rank_num)
      return u"{points} point{s} <small>(rank: {ordinal})</small>".format(
        points=pretty_points(points),
        s="s" if points != '1' else "",
        ordinal=ordinal,
      )
%>

## Runs on render. Variables set in here are not accessible to <%blocks>. To
## make data available, write it to a key in the empty dict 'attributes', which
## was passed in at template render time.
## <%
## %>

## The rest of the template is blocks or body (an implicit block called body).
## Access any top level variables passed in as render args, including the dict
## 'attributes' mentioned in the <% %> section comments above.
<%block name="title">
  ${player}
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1>
        ${player}<br>
        <small class="text-muted">
            Overall rank:
            <a href="${XXX_TOURNEY_BASE}/all-players-ranks.html">
              ${overall_rank}
              <small>
                of ${total_number_of_players}
              </small>
            </a>
        </small>
      </h1>
      % if clan_name is not None:
      <p>
        Clan: <a href="clans/${html.slugify(clan_name)}.html">${clan_name}</a>. Members: ${html.english_join(clan_members)}.
      </p>
      % endif
    </div>
  </div>

  <hr>

  <div class="row">
    <div class="col">
      <h2>Recent Games</h2>
      ${html.full_games_table(
          query.find_games(cursor, player = player, sort_max = 'end_time', limit = 10),
          count=False, win=False,
          excluding=("race", "class", "title", "turns", "duration", "runes", "turns"),
          including=[[1, ('charabbrev', 'Char')], [8, ('src', 'Server')]]
        )}
    </div>
  </div>

  <hr>

  <div class="row">
    <div class="col">
      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item" role="presentation">
          <a class="nav-link active" id="individual-categories-tab" data-toggle="tab" href="#individual-categories" role="tab" aria-controls="individual-categories" aria-selected="true">Individual Categories</a>
        </li>
        % if clan_name is not None:
        <li class="nav-item" role="presentation">
          <a class="nav-link" id="clan-categories-tab" data-toggle="tab" href="#clan-categories" role="tab" aria-controls="clan-categories" aria-selected="false">Clan Categories</a>
        </li>
        % endif
        <li class="nav-item" role="presentation">
          <a class="nav-link" id="banners-tab" data-toggle="tab" href="#banners" role="tab" aria-controls="banners" aria-selected="false">Banners</a>
        </li>
      </ul>
    </div>
  </div>
  <div class="row justify-content-center">
    <div class="col-11">
      <div class="tab-content">
        <div class="tab-pane show active" id="individual-categories" role="tabpanel" aria-labelledby="individual-categories-tab">
          <%include file="player-individual-categories.mako" args="rank_description=rank_description"/>
        </div>
        % if clan_name is not None:
        <div class="tab-pane" id="clan-categories" role="tabpanel" aria-labelledby="clan-categories-tab">
          <%include file="player-clan-categories.mako" args="rank_description=rank_description"/>
        </div>
        % endif
        <div class="tab-pane" id="banners" role="tabpanel" aria-labelledby="banners-tab">
          <%include file="player-banners.mako"/>
        </div>
      </div>
    </div>
  </div>
</%block>
