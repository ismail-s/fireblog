<%inherit file="navbar.mako"/>

<%block name="head">
${parent.head()}
<link rel="stylesheet" href="${request.get_bower_url('simplemde/dist/simplemde.min.css')}">
<script src="${request.get_bower_url('simplemde/dist/simplemde.min.js')}"></script>
</%block>

<%block name="header">${title}</%block>

<%block name="content">

<form id = "edit-post" action = "${save_url}" method = "post">
    <div class="form-group">
        <label for="main-post">Post content</label>
        <textarea name = "body" id="post-content" autofocus = "true"
                cols = "80" rows = "10"
                placeholder = "enter text here"
                id="main-post"
                class = "form-control">${post_text}</textarea>
    </div>
    <div class="form-group">
        <label for="tags">Tags (optional)</label>
        <input type="text" name = "tags"
        id="tags"
        placeholder = "enter any tags here, separated by commas"
        value = "${tags}"
        class="form-control">
    </div>
    <div class="form-group">
        <input type = "submit" name = "form.submitted"
            value = "Submit" class = "form-control"/>
    </div>
</form>

<script>
new SimpleMDE({ element: document.getElementById("post-content") });
</script>

</%block>
