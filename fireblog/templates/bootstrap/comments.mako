<div class="panel-heading">
            <h2 style = "text-align: center">Comments</h2>
        </div>
% if comments:
        <div class = "comments">
% for comment in comments[:-1]:
            <small>Posted ${comment['created']} by ${comment['author']}.</small>
            <p>${comment['comment']}</p>
% if 'g:admin' in request.effective_principals:
            <p><a href="${request.route_url('comment_del', _query = {'comment-uuid': comment['uuid'],'post-id': id})}">Delete this comment</a></p>
% endif
            <hr>
% endfor
            <small>Posted ${comments[-1]['created']} by ${comments[-1]['author']}.</small>
            <p>${comments[-1]['comment']}</p>
% if 'g:admin' in request.effective_principals:
            <p><a href="${request.route_url('comment_del', _query = {'comment-uuid': comments[-1]['uuid'],'post-id': id})}">Delete this comment</a></p>
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
        <input type="hidden" name="post-id" value="${id}">
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
        <input type="hidden" name="post-id" value="${id}">
        <div class="form-group">
            <div class="g-recaptcha" data-sitekey="6LdPugUTAAAAAFJMGiJpfvFjXwPTqVk0mIV9EnrD"></div>
        </div>
        <div class="form-group">
            <input type = "submit" name = "form.submitted"
            value = "Submit" class = "form-control"/>
        </div>
        </form>
% endif