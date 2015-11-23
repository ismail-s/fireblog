<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">


    <title>${settings_dict['persona.siteName']}</title>

    <%block name="head">
    <script src="${request.get_bower_url('webcomponentsjs/webcomponents-lite.min.js')}">
    </script>
    <link href='//fonts.googleapis.com/css?family=Ubuntu' rel='stylesheet' type='text/css'>
    <!-- Custom styles for this template -->
    <style is="custom-style">
        <%include file="polymer-custom-theme.css.mako"/>
    </style>
    <link rel="import" href="${request.get_bower_url('paper-toolbar/paper-toolbar.html')}">
    <link rel="import" href="${request.get_bower_url('paper-scroll-header-panel/paper-scroll-header-panel.html')}">
    <link rel="import" href="${request.get_bower_url('paper-material/paper-material.html')}">
    <link rel="import" href="${request.get_bower_url('paper-toast/paper-toast.html')}">
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="//oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    <script src='//www.google.com/recaptcha/api.js'></script>
    </%block>
  </head>
  <body>

  % for error in request.session.pop_flash():
    <paper-toast class="toast-alert" duration=2000>${error}</paper-toast>
  % endfor
  <script>
  var showToasts = function(event) {
    // Get all the toast elements.
    var elems = Array.prototype.slice.call(document.getElementsByClassName('toast-alert'));
    var showElem = function(array){
      // Show toast.
      array[0].show();
      if (array.length > 1) {
        // Show the next toast once the first one has disappeared.
        setTimeout(showElem, 2000, array.slice(1));
    }};
    showElem(elems);
  }
  window.addEventListener('load', showToasts, false);
  </script>


  <%block name="main_body">
    <paper-scroll-header-panel>
        <paper-toolbar class="header">
            <%block name = "header_toolbar">
            <div class="title-text flex-1"><h1>${settings_dict['persona.siteName']}</h1></div>
            <div><h1>${request.persona_button}</h1></div>
            </%block>
        </paper-toolbar>
        <div class="margin-20">
            <h1 class="center"><%block name = "header"/></h1>
            <%block name = "content"/>
            <footer><a href = "${request.route_url('rss')}">rss</a></footer>
        </div>
    </paper-scroll-header-panel>
    </%block>
    <%block name="footer_js">
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.js"></script>
    <script src="//login.persona.org/include.js" type="text/javascript"></script>
    <script type="text/javascript">${request.persona_js}</script>
    </%block>
  </body>
</html>
