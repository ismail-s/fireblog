<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">

<%
if code_styles:
     from pygments.formatters import HtmlFormatter
     extra_styles = HtmlFormatter.get_style_defs(HtmlFormatter())
else:
    extra_styles = None
%>

% if extra_styles:
<style>
${extra_styles}
</style>
% endif

<%
if request.matched_route.name == 'tag_view':
    tag_name = request.matchdict['tag_name']
    sort_old_url = request.route_url('tag_view', tag_name=tag_name, _query=(('p', page_num), ('sort-ascending', 'true')))
    sort_new_url = request.route_url('tag_view', tag_name=tag_name, _query=[('p', page_num)])
else:
    sort_old_url = request.route_url(request.matched_route.name, _query=(('p', page_num), ('sort-ascending', 'true')))
    sort_new_url = request.route_url(request.matched_route.name, _query=[('p', page_num)])
%>
<div class="btn-group">
  <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
    Sort Order <span class="caret"></span>
  </button>
  <ul class="dropdown-menu">
    <li><a href="${sort_old_url}">Oldest First</a></li>
    <li><a href="${sort_new_url}">Newest First</a></li>
  </ul>
</div>
<div class="center">${pager|n}</div>

% for post in posts:
<div class = "panel panel-default">
    <div class = "panel-heading all-posts-header">
    <a href = "${request.route_url('view_post', id=post["id"], postname = urlify(post["name"]))}">
        <h2>
                ${post["name"]} <small>Created ${post["date"]}</small>
        </h2>
    </a>
    </div>
    <div class="panel-body">
        ${post["html"]|n}
    </div>
</div>
</a>
% endfor

<div class="center">${pager|n}</div>


% if uuid:
<p style="text-align: center"><small>
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
% endif

</%block>
