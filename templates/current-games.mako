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
      <h2>
        Ongoing Games
      </h2>
    </div>
  </div>

  <div class="row">
    <div class="col">
	${html.whereis_table(attributes['cursor'])}
    </div>
  </div>
</%block>
