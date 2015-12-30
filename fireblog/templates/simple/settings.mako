<%inherit file="navbar.mako"/>

<%block name="header">Settings</%block>

<%block name="content">
    <form id="change-settings" action="${save_url}" method="post">
        % for entry in mapping:
            % if entry.min or entry.max:
                <input type="number"
                % if entry.min:
                    min="${entry.min}"
                % endif
                % if entry.max:
                    max="${entry.max}"
                % endif
            % else:
                <input type="text" charCounter
            % endif
            id="${entry.registry_name}"
            name="${entry.registry_name}"
            label="${entry.display_name}"
            value="${entry.value}"
            style="width: 100%"
            required auto-validate></input>
            <p>${entry.description}</p>

        % endfor
        <input type="submit" value="Submit"</input>
        </form>
    </%block>
