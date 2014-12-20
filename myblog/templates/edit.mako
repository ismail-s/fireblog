<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">
<form action = "${save_url}" method = "post">
    <div class="form-group">
        <textarea name = "body" autofocus = "true"
                cols = "80" rows = "10"
                placeholder = "enter text here"
                class = "form-control">${post_text}</textarea>
    </div>
    <div class="form-group">
        <input type = "submit" name = "form.submitted" value = "Submit" class = "form-control"/>
    </div>
</form>

</%block>
