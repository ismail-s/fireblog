body {
  padding: 0px;
  margin: 0px;
  height: 100vh;
  font-family: 'Ubuntu', sans-serif;
  background-color: #f5f5f5;/*--google-grey-100*/
}

a, a:hover, a:visited {
  color: inherit;
}

a:hover, a:hover > h1 {
  opacity: 0.9;
}

h1 {
  margin: 0.2em;
}

h2 {
  margin: 0.1em;
}

.center {
  text-align: center;
}

.post {
    text-align: left;
}

.all-posts-header {
    text-align: center;
}

footer {
    text-align: center;
    padding-bottom: 5px;
}

paper-scroll-header-panel {
  height: 100%;
}

paper-header-panel {
  width: 100vw;
}

paper-fab {
    position: fixed;
    bottom: 16px;
    right: 16px;
}

paper-dialog {
  padding: 0px 5px;
}

.starter-template {
  padding: 40px 15px;
  text-align: center;
}

.header {
  --paper-toolbar-background: #db4437;/*--google-red-500*/
  color: white;
}

% if request.authenticated_userid:
.title-text > h1 {
  font-size: 1em;
  font-weight: normal;
}

% else:
.title-text > h1 {
  font-size: 1.6em;
}
% endif

.card {
  background: white;
  padding: 2px 7px 8px;
  margin: 8px 0px;
}

paper-button.blue {
  background: #4285f4;/*--google-blue-500*/
  color: white;
}

paper-button.red {
  background: #db4437;/*--google-red-500*/
  color: white;
}

.margin-20 {
  margin: 20px;
}

.flex, .flex-horizontal-wrap, .flex-horizontal-center, .flex-vertical {
  display: -ms-flexbox;
  display: -webkit-flex;
  display: flex;
}

.flex-horizontal-wrap, .flex-horizontal-center {
  -ms-flex-direction: row;
  -webkit-flex-direction: row;
  flex-direction: row;
  @apply(--layout-horizontal);
}

.flex-horizontal-wrap {
  flex-wrap: wrap;
}

.flex-horizontal-center {
  justify-content: center;
}

.flex-vertical {
  -ms-flex-direction: column;
  -webkit-flex-direction: column;
  flex-direction: column;
  @apply(--layout-vertical);
}
.flex-1 {
  flex: 1;
}
