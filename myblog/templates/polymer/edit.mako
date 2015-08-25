<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="head">
${parent.head()}
<link rel="import" href="${request.static_url('myblog:static/form-submit.html')}">
<link rel="import" href="${request.get_bower_url('paper-input/paper-input.html')}">
<link rel="import" href="${request.get_bower_url('paper-input/paper-textarea.html')}">
</%block>

<%block name="content">
<paper-material class="card" elevation = "2">
    <form id = "edit-post" action = "${save_url}" method = "post">
        <label for="body">Post content</label>
        <paper-textarea name = "body" autofocus = "true"
            label="Enter the post content here"
            value="${post_text}"
            id="main-post"></paper-textarea>
        <label for="tags">Tags (optional)</label>
        <paper-input name = "tags"
            id="tags"
            label = "enter any tags here, separated by commas"
            value = "${tags}"></paper-input>
        <input type="hidden" name="form.submitted">
        <form-submit-button>Submit</form-submit-button>
    </form>
</paper-material>
</%block>
