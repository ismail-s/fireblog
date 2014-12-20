<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">
${html|n}

<ul class="pager">

% if prev_page:
  <li><a href="${prev_page}">Older</a></li>
% endif

% if next_page:
  <li><a href="${next_page}">Newer</a></li>
% endif

</ul>

</%block>
