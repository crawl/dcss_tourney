<%!
  import nemelex
  import html
%>

<%
  nem_list = nemelex.list_nemelex_choices(cursor)
  pnem_list = []
  if nem_list:
    for x in nem_list[:-1]:
      combostr = '<b>' + x[0] + '</b> (won:'
      if x[2] >= 9:
        combostr += ' <s>%d individual</s>,' % x[2]
      else:
        combostr += ' %d individual,' % x[2]
      if x[3] >= 9:
        combostr += ' <s>%d clan</s>' % x[3]
      else:
        combostr += ' %d clan' % x[3]
      combostr += ')'
      pnem_list.append(combostr)
%>
% if nem_list:
<p class="lead">
  Current combo:
  <code>${nem_list[-1][0]}</code>. Chosen on ${nem_list[-1][1]} UTC.
</p>
% endif
% if pnem_list:
<p>
  Previous combos:
  ${html.english_join(pnem_list)}
</p>
% endif
