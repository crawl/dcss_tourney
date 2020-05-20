<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  from crawl_utils import MAX_CATEGORY_SCORE

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
    return '%s%s' % (num, suffix)

  def points_for_rank(rank_num):
    if rank_num == 0:
      return "-"
    return str(int(round(MAX_CATEGORY_SCORE / rank_num, 0)))

  def rank_description(rank_num):
    if rank_num == 0:
      return u"0 points<br><small>(rank: ∞)</small>"
    else:
      points = points_for_rank(rank_num)
      ordinal = rank_ordinal(rank_num)
      return "{points} point{s}<br><small>(rank: {ordinal})</small>".format(
        points=points,
        s="s" if points != '1' else "",
        ordinal=ordinal,
      )
%>

## Runs on render. Variables set in here are not accessible to <%blocks>. To
## make data available, write it to a key in the empty dict 'attributes', which
## was passed in at template render time.
<%
%>

<%block name="title">
  ${player}
</%block>

<%block name="body">
  <div class="row">
    <h1>
      ${player}<br>
      <small class="text-muted">Overall rank: ${overall_rank} <small>of ${total_number_of_players}</small></small>
    </h1>
  </div>

  <div class="row">
    <h2>Categories</h2>
  </div>
  % for category in categories:
  <%
    import html
    name = category['name']
    css_class = "category-%s" % slugify(name)
    rank_desc = rank_description(category['player_rank'])
  %>
  <div class="row">
    <div class="jumbotron jumbotron-fluid category ${css_class} text-light p-3">
      <h2 class="text-outline-black-1">${name}</h2>
      <div class="row">
        <div class="col col-sm-4">
          <h3 class="text-outline-black-1">${rank_desc}</h3>
        </div>
        <div class="col-sm">
          <p class="d-none d-sm-block">
            <i>${category['desc']}</i>
          </p>
          <p class="lead">
            ${category['rank_details']}
          </p>
        </div>
      </div>
    </div>
  </div>
  % endfor
</%block>
