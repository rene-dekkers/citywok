{% macro start(title, striped=false) -%}
<div class="panel panel-default">
	<div class="panel-heading">{{ title }}</div>
	<table class="table{% if striped == true %} table-striped{% endif %}">
{%- endmacro -%}

{% macro end() -%}
	</table>
</div>
{%- endmacro -%}

{% macro row(head=false) -%}
{% if head %}<thead>{% endif %}
<tr>
{%- endmacro -%}

{% macro endrow(head=false) -%}
</tr>
{% if head %}</thead>{% endif %}
{%- endmacro -%}

{% macro column(value, align=none, colspan=0) -%}
<td{% if align != none %} align="{{ align | e }}"{% endif %}{% if colspan > 0 %} colspan="{{ colspan }}"{% endif %}>{{ value | e }}</td>
{% endmacro %}

{% macro head(value, align=none) -%}
<th{% if align != none %} class="{{ align |e }}"{% endif %}>{{ value | e }}</th>
{% endmacro %}
