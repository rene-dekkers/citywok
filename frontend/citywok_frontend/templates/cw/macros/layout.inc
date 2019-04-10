{% macro page_title(titlestr) -%}
<center><h1>{{ titlestr | title | e }}</h1></center>
{%- endmacro -%}

{% macro icon(iconstr, title=none) -%}
<span class="fa fa-{{ iconstr | e }}"{% if title != none %} title="{{ title | e }}" data-toggle="tooltip"{% endif %}></span>
{%- endmacro -%}

{% macro thumbnail(content, title=none) -%}
<div class="thumbnail">
	{% if title != none %}
	<div class="caption">
	<h3>{{ title | e }}</h3>
	</div>
	{% endif %}
{{ content | e }}
</div>
{%- endmacro -%}

{% macro image(filename, class=none) -%}
<img src="{{ filename | e }}" class="img-responsive{% if class != none %} {{ class | e }}{% endif %}" />
{%- endmacro -%}

{% macro virtual_state(virtual, state) %}
	{%- import 'cw/macros/layout.inc' as layout -%}
	<div class="btn-group">
		<button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
		{{ layout.icon('power-off', title=_('set machine state') | title) }}&nbsp;{{ _('set machine state') | title }}
		</button>
		<ul class="dropdown-menu">
			<li{% if state == 'running' %} class="active"{% endif %}>
				<a href="javascript:update_state('{{ virtual | e }}', 'running')">{{ _('running') | title }}</a>
			</li>
			<li{% if state in ['shutdown','shutoff'] %} class="active"{% endif %}>
				<a href="javascript:update_state('{{ virtual | e }}', 'shutdown')">{{ _('shutdown') | title }}</a>
			</li>
			<li{% if state == 'paused' %} class="active"{% endif %}>
				<a href="javascript:update_state('{{ virtual | e }}', 'paused')">{{ _('paused') | title }}</a>
			</li>
			<li{% if state == 'resumed' %} class="active"{% endif %}>
				<a href="javascript:update_state('{{ virtual | e }}', 'resume')">{{ _('resume') | title }}</a>
			</li>
		</ul>
	</div> 
{% endmacro %}
