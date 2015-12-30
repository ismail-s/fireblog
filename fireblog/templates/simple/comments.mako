<h2 style = "text-align: center">Comments</h2>
% for comment in comments:
    <div>${comment['comment']}</div>
    <div>Posted ${comment['created']} by ${comment['author']}.
        % if 'g:admin' in request.effective_principals:
            <a href="${request.route_url('comment_del', _query = {'comment-uuid': comment['uuid'],'post-id': post_id})}">Delete this comment</a>
        % endif
    </div>
    <hr>
% endfor

% if request.authenticated_userid:  # All authenticated users can comment.
<form id = "add-comment" action = "${comment_add_url}" method = "post">
    <textarea name = "comment"
        placeholder = "enter your comment here"
        id="add-comment"
        label="Add a comment"
        style="width: 100%"></textarea>
    <paper-button raised><input type="hidden" name="post-id" value="${post_id}">
    <input type = "hidden" name = "form.submitted">
    <input type="submit" value="Submit"></input>
</form>
% else:

    ## Sort out comment add anonymous url
    <form id = "add-comments" name="add-comment" action = "${comment_add_url}" method = "post">
        <textarea
            name="comment"
            placeholder = "enter your comment here"
            id="add-comment"
            label="Add a comment anonymously."
            style="width: 100%"></textarea>
        <br/>
        <label>\
            If you want to keep track of your comments, and have\
            your own name, then click the "Sign in" button at the top of the page to\
            sign in (we magically create an account for you behind the scenes).\
        </label>
        <input type="hidden" name="post-id" value="${post_id}">
        <input type="hidden" name="form.submitted">
        <div class="g-recaptcha" data-sitekey="${settings_dict['fireblog.recaptcha_site_key']}"></div>
        <input type="submit" value="Submit"></input>
    </form>
% endif
