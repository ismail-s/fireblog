<h2 style = "text-align: center">Comments</h2>
% for comment in comments:
    <paper-item><paper-item-body two-line>
        <div style="white-space: normal;">${comment['comment']}</div>
        <div secondary>Posted ${comment['created']} by ${comment['author']}.
    % if 'g:admin' in request.effective_principals:
            <a href="${request.route_url('comment_del', _query = {'comment-uuid': comment['uuid'],'postname': post_title})}">Delete this comment</a>
    % endif
        </div>
    </paper-item-body></paper-item>
% endfor

% if request.authenticated_userid:  # All authenticated users can comment.
        <form id = "add-comment" action = "${comment_add_url}" method = "post">
            <paper-textarea name = "comment"
            placeholder = "enter your comment here"
            id="add-comment"
            label="Add a comment"
            class = "form-control"></paper-textarea>
        <paper-button raised><input type="hidden" name="postname" value="${post_title}">
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
        <input type="hidden" name="postname" value="${post_title}">
        <input type="hidden" name="form.submitted">
            <div class="g-recaptcha" data-sitekey="6LdPugUTAAAAAFJMGiJpfvFjXwPTqVk0mIV9EnrD"></div>
            <form-submit-button>Submit</form-submit-button>
        </form>
% endif