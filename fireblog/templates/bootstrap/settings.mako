<%inherit file="navbar.mako" />

<%block name="header">Settings</%block>

<%block name="content">
<form id = "change-settings" action = "${save_url}" method = "post">

% for entry in mapping:

    <div class="form-group">
        <label for="${entry.registry_name}">${entry.display_name}</label>
        <span class="help-block">${entry.description}</span>
    % if entry.min or entry.max:
        <input type="number" class="form-control"
        % if entry.min:
            min="${entry.min}"
        % endif
        % if entry.max:
            max="${entry.max}"
        % endif
    % else:
        <input type="text" class="form-control"
    % endif
            id="${entry.registry_name}"
            name="${entry.registry_name}"
            placeholder="${entry.display_name}"
            required>
    </div>

% endfor
    <button type="submit" class="btn btn-default">Submit</button>
</form>

</%block>