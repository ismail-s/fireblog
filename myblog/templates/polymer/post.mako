<%inherit file="navbar.mako"/>

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

<paper-material class="card" elevation = "2">
<h1 class="center">${title}</h1>
<div class = "post">${html|n}</div>

<p style="text-align: center"><small>Created ${post_date}.
% if tags:
Tags: ${tags|n}
% endif
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
<div class="flex-horizontal-center">

% if prev_page:
  <a href="${prev_page}"><paper-button raised class="button-blue">Older</paper-button></a>
% endif

<a href="${request.route_url('view_all_posts')}"><paper-button raised>All Posts</paper-button></a>

% if next_page:
  <a href="${next_page}"><paper-button raised class="button-blue">Newer</paper-button></a>
% endif

</div>
</paper-material>


<paper-material class="card">
    <h2 style = "text-align: center">Comments</h2>
% if comments:
% for comment in comments[:-1]:
    <paper-item><paper-item-body two-line>
        <div>${comment['comment']}</div>
        <div secondary>Posted ${comment['created']} by ${comment['author']}.
% if 'g:admin' in request.effective_principals:
            <a href="${request.route_url('comment_del', _query = {'comment-uuid': comment['uuid'],'postname': title})}">Delete this comment</a>
% endif
        </div>
    </paper-item-body></paper-item>
% endfor
    <paper-item><paper-item-body two-line>
        <div>${comments[-1]['comment']}</div>
        <div secondary>Posted ${comments[-1]['created']} by ${comments[-1]['author']}.
% if 'g:admin' in request.effective_principals:
            <a href="${request.route_url('comment_del', _query = {'comment-uuid': comments[-1]['uuid'],'postname': title})}">Delete this comment</a>
% endif
        </div>
    </paper-item-body></paper-item>
% endif

% if request.authenticated_userid:  # All authenticated users can comment.
        <form id = "add-comment" action = "${comment_add_url}" method = "post">
            <paper-textarea name = "comment"
            placeholder = "enter your comment here"
            id="add-comment"
            label="Add a comment"
            class = "form-control"></paper-textarea>
        <paper-button raised><input type="hidden" name="postname" value="${title}">
            <input type = "hidden" name = "form.submitted">
            <form-submit-button>Submit</form-submit-button>
        </form>
% else:

## Sort out comment add anonymous url
        <form id = "add-comments" name="add-comment" action = "${comment_add_url}" method = "post">
            <paper-textarea
            name="comment"
            placeholder = "enter your comment here"
            id="add-comment"
            label="Add a comment anonymously."
            class = "form-control"></paper-textarea>
            <label>\
If you want to keep track of your comments, and have\
 your own name, then click the "Sign in" button at the top of the page to\
 sign in (we magically create an account for you behind the scenes).\
            </label>
        <input type="hidden" name="postname" value="${title}">
        <input type="hidden" name="form.submitted">
            <div class="g-recaptcha" data-sitekey="6LdPugUTAAAAAFJMGiJpfvFjXwPTqVk0mIV9EnrD"></div>
            <form-submit-button>Submit</form-submit-button>
        </form>
% endif
</paper-material>
</%block>
