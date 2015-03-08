<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">

<%
if 'class="codehilite"' in html:
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

<div class = "post">
${html|n}
</div>

<p style="text-align: center"><small>Created ${post_date}.
% if tags:
Tags: ${tags|n}
% endif
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
<ul class="pager">

% if prev_page:
  <li><a href="${prev_page}">Older</a></li>
% endif

<li><a href="${request.route_url('view_all_posts')}">All Posts</a></li>

% if next_page:
  <li><a href="${next_page}">Newer</a></li>
% endif

</ul>

% if comments or request.authenticated_userid:
<div class="panel">
<div class="panel-body">
<div class="panel-heading"><h2 style = "text-align: center">Comments</h2></div>
% if comments:
<div class = "comments">
% for comment in comments[:-1]:
<small>Posted ${comment['created']} by ${comment['author']}.</small>
<p>${comment['comment']}</p>
<hr>
% endfor
<small>Posted ${comments[-1]['created']} by ${comments[-1]['author']}.</small>
<p>${comments[-1]['comment']}</p>
</div>
% endif

% if request.authenticated_userid:
<form id = "add-comment" action = "${comment_add_url}" method = "post">
    <div class="form-group">
        <label for="add-comment">Post content</label>
        <textarea name = "comment"
                cols = "70" rows = "5"
                placeholder = "enter your comment here"
                id="add-comment"
                class = "form-control"></textarea>
    </div>
    <input type="hidden" name="postname" value="${title}">
    <div class="form-group">
        <input type = "submit" name = "form.submitted"
            value = "Submit" class = "form-control"/>
    </div>
</form>
% endif
</div>
</div>
% endif
</%block>
