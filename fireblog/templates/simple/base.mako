<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="description" content="">
        <meta name="author" content="">


        <title>${settings_dict['persona.siteName']}</title>

        <%block name="head">
            <script src='//www.google.com/recaptcha/api.js'></script>
        </%block>
    </head>
    <body>

        % for error in request.session.pop_flash():
            <div>${error}</div>
        % endfor

        <%block name="main_body">
            <%block name = "header_toolbar">
                <div>
                    <b>${settings_dict['persona.siteName']} ${request.persona_button}</b>
                </div>
            </%block>

            <h2><%block name = "header"/></h2>
            <%block name = "content"/>
            <footer><a href = "${request.route_url('rss')}">rss</a></footer>
        </%block>
        <%block name="footer_js">
            <!-- Placed at the end of the document so the pages load faster -->
            <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.js"></script>
            <script src="//login.persona.org/include.js" type="text/javascript"></script>
            <script type="text/javascript">${request.persona_js}</script>
        </%block>
    </body>
</html>
