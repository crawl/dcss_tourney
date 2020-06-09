<%inherit file="base.mako"/>

<%!
  import html
  active_menu_item = "Ongoing Games"
%>

<%block name="title">
  Ongoing Games
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1 class="display-1">
        Ongoing Games
      </h1>
    </div>
  </div>

  <div class="row">
    <div class="col">
	${html.whereis_table(attributes['cursor'])}
    </div>
  </div>
</%block>
