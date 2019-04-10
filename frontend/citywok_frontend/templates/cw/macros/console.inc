{%- import 'cw/macros/layout.inc' as layout -%}
{% macro spice_includes() -%}
<script src="{{ url_for('static', filename='spice-html5/spicearraybuffer.js') }}"></script> 
<script src="{{ url_for('static', filename='spice-html5/enums.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/atKeynames.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/utils.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/png.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/lz.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/quic.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/bitmap.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/spicedataview.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/spicetype.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/spicemsg.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/wire.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/spiceconn.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/display.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/main.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/inputs.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/webm.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/playback.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/simulatecursor.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/cursor.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/thirdparty/jsbn.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/thirdparty/rsa.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/thirdparty/prng4.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/thirdparty/rng.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/thirdparty/sha1.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/ticket.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/resize.js') }}"></script>
<script src="{{ url_for('static', filename='spice-html5/filexfer.js') }}"></script>
<!--<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='spice-html5/spice.css') }}" />-->
{%- endmacro -%}

{%- macro spice_connect_meuk(ws_uri) %}
        <script>
            var host = null, port = null;
            var sc;

            function spice_set_cookie(name, value, days) {
                var date, expires;
                date = new Date();
                date.setTime(date.getTime() + (days*24*60*60*1000));
                expires = "; expires=" + date.toGMTString();
                document.cookie = name + "=" + value + expires + "; path=/";
            };

            function spice_query_var(name, defvalue) {
                var match = RegExp('[?&]' + name + '=([^&]*)')
                                  .exec(window.location.search);
                return match ?
                    decodeURIComponent(match[1].replace(/\+/g, ' '))
                    : defvalue;
            }

            function spice_error(e)
            {
                disconnect();
            }

            function connect()
            {
                var host, port, password, scheme = "ws://", uri;

                // By default, use the host and port of server that served this file
                host = spice_query_var('host', window.location.hostname);

                // Note that using the web server port only makes sense
                //  if your web server has a reverse proxy to relay the WebSocket
                //  traffic to the correct destination port.
                var default_port = window.location.port;
                if (!default_port) {
                    if (window.location.protocol == 'http:') {
                        default_port = 80;
                    }
                    else if (window.location.protocol == 'https:') {
                        default_port = 443;
                    }
                }
                port = spice_query_var('port', default_port);
                if (window.location.protocol == 'https:') {
                    scheme = "wss://";
                }

                // If a token variable is passed in, set the parameter in a cookie.
                // This is used by nova-spiceproxy.
                token = spice_query_var('token', null);
                if (token) {
                    spice_set_cookie('token', token, 1)
                }

                password = spice_query_var('password', '');
                path = spice_query_var('path', 'websockify');

                if ((!host) || (!port)) {
                    console.log("must specify host and port in URL");
                    return;
                }

                if (sc) {
                    sc.stop();
                }

                uri = '{{ ws_uri | e }}';

                try
                {
                    sc = new SpiceMainConn({uri: uri, screen_id: "spice-screen", dump_id: "debug-div",
                                message_id: "message-div", password: password, onerror: spice_error, onagent: agent_connected });
                }
                catch (e)
                {
                    alert(e.toString());
                    disconnect();
                }

            }

            function disconnect()
            {
                console.log(">> disconnect");
                if (sc) {
                    sc.stop();
                }
                if (window.File && window.FileReader && window.FileList && window.Blob)
                {
                    var spice_xfer_area = document.getElementById('spice-xfer-area');
                    document.getElementById('spice-area').removeChild(spice_xfer_area);
                    document.getElementById('spice-area').removeEventListener('dragover', handle_file_dragover, false);
                    document.getElementById('spice-area').removeEventListener('drop', handle_file_drop, false);
                }
                console.log("<< disconnect");
            }

            function agent_connected(sc)
            {
                window.addEventListener('resize', handle_resize);
                window.spice_connection = this;

                resize_helper(this);

                if (window.File && window.FileReader && window.FileList && window.Blob)
                {
                    var spice_xfer_area = document.createElement("div");
                    spice_xfer_area.setAttribute('id', 'spice-xfer-area');
                    document.getElementById('spice-area').appendChild(spice_xfer_area);
                    document.getElementById('spice-area').addEventListener('dragover', handle_file_dragover, false);
                    document.getElementById('spice-area').addEventListener('drop', handle_file_drop, false);
                }
                else
                {
                    console.log("File API is not supported");
                }
            }

            connect();
        </script>
{%- endmacro -%}

{%- macro spice_screen(virtual) -%}
<div class="btn-group">
	<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{{ layout.icon('bars', title=_('Keyboard keys') | title) }}</button>
	<ul class="dropdown-menu">
		<li><a href="{{ url_for('virtual', virtual=virtual['name'])+'/screenshot' }}" class="white" target="_blank">{{ layout.icon('camera') }}&nbsp;{{ _('screenshot') | title }}</a></li>
<!--		<li><a href="javascript:sendCtrlAltDel()">{{ layout.icon('keyboard-o') }}&nbsp;{{ _('Send ctrlaltdel') | title }}</a></li>-->
	</ul>
</div> 

<div id="spice-area">
	<div id="spice-screen" class="spice-screen"></div>
</div>
<div id="message-div" class="spice-message" style="display:none"></div>
<div id="debug-div" style="display:none"></div>
{%- endmacro -%}

{%- macro spice_screen_notrunning(virtual) -%}
<div id="spice-area" class="">
	<div id="spice-screen" class="spice-screen"><div class="console-not-running"><h2>{{ virtual['state'] | title | e }}</h2></div></div>
</div>
<div id="message-div" class="spice-message" style="display:none"></div>
<div id="debug-div" style="display:none"></div>
{%- endmacro -%}
