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

<div class="panel">
    <div class="panel-body">
        <div class="panel-heading">
            <h2 style = "text-align: center">Comments</h2>
        </div>
% if comments:
        <div class = "comments">
% for comment in comments[:-1]:
            <small>Posted ${comment['created']} by ${comment['author']}.</small>
            <p>${comment['comment']}</p>
% if 'g:admin' in request.effective_principals:
            <p><a href="${request.route_url('comment_del', _query = {'comment-uuid': comment['uuid'],'postname': title})}">Delete this comment</a></p>
% endif
            <hr>
% endfor
            <small>Posted ${comments[-1]['created']} by ${comments[-1]['author']}.</small>
            <p>${comments[-1]['comment']}</p>
% if 'g:admin' in request.effective_principals:
            <p><a href="${request.route_url('comment_del', _query = {'comment-uuid': comments[-1]['uuid'],'postname': title})}">Delete this comment</a></p>
% endif
        </div>
% endif

% if request.authenticated_userid:  # All authenticated users can comment.
        <form id = "add-comment" action = "${comment_add_url}" method = "post">
        <div class="form-group">
            <label for="add-comment">Add a comment</label>
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
% else:

## Sort out comment add anonymous url
        <form id = "add-comments" action = "${comment_add_url}" method = "post">
        <div class="form-group">
            <label for="add-comment">Add a comment anonymously.</label>
            <textarea name = "comment"
            cols = "70" rows = "5"
            placeholder = "enter your comment here"
            id="add-comment"
            class = "form-control"></textarea>
            <label>\
If you want to keep track of your comments, and have\
 your own name, then click the "Sign in" button at the top of the page to\
 sign in (we magically create an account for you behind the scenes).\
            </label>
        </div>
        <input type="hidden" name="postname" value="${title}">
        <div class="form-group">
            <div class="g-recaptcha" data-sitekey="6LdPugUTAAAAAFJMGiJpfvFjXwPTqVk0mIV9EnrD"></div>
        </div>
        <div class="form-group">
            <input type = "submit" name = "form.submitted"
            value = "Submit" class = "form-control"/>
        </div>
        </form>
% endif
    </div>
</div>
</%block>
