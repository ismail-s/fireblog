<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">


    <title>Not the answer--a blog</title>

    <script src="${request.get_bower_url('webcomponentsjs/webcomponents-lite.min.js')}">
    </script>
    <link href='http://fonts.googleapis.com/css?family=Ubuntu' rel='stylesheet' type='text/css'>
    <!-- Custom styles for this template -->
    <style>
        <%include file="myblog:static/polymer-custom-theme.css"/>
    </style>
    <link rel="import" href="${request.get_bower_url('iron-flex-layout/iron-flex-layout.html')}">
    <link rel="import" href="${request.get_bower_url('paper-button/paper-button.html')}">
    <link rel="import" href="${request.get_bower_url('paper-item/paper-item.html')}">
    <link rel="import" href="${request.get_bower_url('paper-item/paper-item-body.html')}">
    <link rel="import" href="${request.get_bower_url('paper-input/paper-textarea.html')}">
    <link rel="import" href="${request.get_bower_url('paper-header-panel/paper-header-panel.html')}">
    <link rel="import" href="${request.get_bower_url('paper-material/paper-material.html')}">
    <link rel="import" href="${request.static_url('myblog:static/form-submit.html')}">
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    <script src='https://www.google.com/recaptcha/api.js'></script>
  </head>
  <body>
    <paper-header-panel mode="scroll">
<%block name = "navbar"/>
    <paper-toolbar>
    <div class="flex-horizontal">
            <div style="flex: 1"><h1>Not the Answer - <small>A personal blog</small></h1></div>
        <div><h1>${request.persona_button}</h1></div>
    </div>
    </paper-toolbar>
    <div class="margin-20">
        <h1><%block name = "header"/></h1>
        <%block name = "content"/>
        <footer><a href = "${request.route_url('rss')}">rss</a></footer>
    </div>
    </paper-header-panel>

    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="https://login.persona.org/include.js" type="text/javascript"></script>
    <script type="text/javascript">${request.persona_js}</script>
    <%block name = "navbar_js"/>
  </body>
</html>
