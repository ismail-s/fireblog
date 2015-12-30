<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">
    <form id="edit-post" action="${save_url}" method="post">
        <label for="body">Post content</label>
        <textarea autofocus="true"
            label="Enter the post content here"
            id="main-post"
            name="body">${post_text}</textarea>
        <label for="tags">Tags (optional)</label>
        <input name="tags"
        id="tags"
        label="enter any tags here, separated by commas"
        value="${tags}"></input>
        <input type="hidden" name="form.submitted">
        <input type="submit" value="Submit">
    </form>
</%block>
