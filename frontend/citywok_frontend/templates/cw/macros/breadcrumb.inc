{% macro start() -%}
<ol class="breadcrumb">
{%- endmacro -%}

{% macro item(inner_html, href=none, active=true) -%}
<li{% if active %} class="active"{% endif %}>{% if href != none %}<a href="{{ href | e }}">{{ inner_html | e }}</a>{% else %}{{ inner_html | e }}{% endif %}</li>
{%- endmacro -%}

{% macro end() -%}
</ol>
{%- endmacro -%}
