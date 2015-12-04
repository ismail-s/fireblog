<%inherit file="navbar.mako"/>

<%block name="head">
${parent.head()}
<link rel="import" href="${request.static_url('fireblog:static/form-submit.html')}">
<link rel="import" href="${get_bower_url('paper-input/paper-input.html')}">
</%block>

<%block name="header">Settings</%block>

<%block name="content">
<paper-material class="card" elevation = "2">
    <form id = "change-settings" action = "${save_url}" method = "post">

% for entry in mapping:
% if entry.min or entry.max:
        <paper-input type="number"
        % if entry.min:
            min="${entry.min}"
        % endif
        % if entry.max:
            max="${entry.max}"
        % endif
    % else:
        <paper-input type="text" charCounter
    % endif
            id="${entry.registry_name}"
            name="${entry.registry_name}"
            label="${entry.display_name}"
            value="${entry.value}"
            required auto-validate></paper-input>
        <p>${entry.description}</p>

% endfor
        <form-submit-button>Submit</form-submit-button>
    </form>
</paper-material>
</%block>
