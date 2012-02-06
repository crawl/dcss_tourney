<%
   import uniq
   hard_uniques = uniq.HARD_UNIQUES
   medium_uniques = uniq.MEDIUM_UNIQUES
   easy_uniques = uniq.EASY_UNIQUES
%>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>Vehumet's headhunting guide</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>

      <div class="page_content">
        <div class="content">

        <h2>Vehumet's headhunting guide</h2>
        <p>
          I: Kill any two uniques within two turns of each other.
        <br>
          II: Kill two medium or deep uniques within one turn of each other.
        <br>
          III: Kill two deep uniques on the same turn.
        </p>
        <hr>
        <h2>Deep Uniques</h2>
        <div class="fineprint">
          Uniques who do not normally generate before depth 18.
        </div>
        <div class="inset">
          ${", ".join(hard_uniques)}
        </div>
        <h2>Medium Uniques</h2>
        <div class="fineprint">
          Uniques who do not normally generate before depth 11 and are not on the previous list.
        </div>
        <div class="inset">
          ${", ".join(medium_uniques)}
        </div>
        <h2>Shallow Uniques</h2>
        <div class="fineprint">
          Uniques who are not on the previous lists.
        </div>
        <div class="inset">
          ${", ".join(easy_uniques)}
        </div>

        </div>
      </div>
    </div>
  </body>
</html>