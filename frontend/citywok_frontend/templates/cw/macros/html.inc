{% macro hyperlink(inner_html, href, name=none, class=none, target=none) -%}
<a href="{{ href |e }}"{% if name != none %} name="{{ name | e }}"{% endif %}{% if class != none %} class="{{ class | e }}"{% endif %}{% if target != none %} target="{{ target | e }}"{% endif %}>{{ inner_html | e }}</a>
{%- endmacro -%}

{% macro button(inner_html, title=none, type='button', disabled=false) -%}
<button type="{{ type }}" class="btn btn-primary"{% if title != none %} title="{{ title | e }}"{% endif %}{% if disabled %} disabled="disabled"{% endif %}>{{ inner_html | e }}</button>
{%- endmacro -%}

{% macro input(name, value='', type='text', size=20) -%}
<input type="{{ type }}" name="{{ name }}" class="form-control" value="{{ value|e }}"{% if size != none %} size="{{ size }}"{% endif %}>
{%- endmacro -%}

{% macro textarea(name, value='', type='text', size=20) -%}
<textarea name="{{ name }}" class="form-control">{{ value }}</textarea>
{%- endmacro -%}

{% macro select(name, label = none, value='', items=[]) -%}
{% if label != none %}
<label for="{{ name | e }}">{{ label | e }}</label>
{% endif %}
<select class="form-control" name="{{ name }}">
{% for i in items %}
	<option value="{{ i | e }}"{% if value == i %} selected="selected"{% endif %}>{{ i | e }}</option>
{% endfor %}
</select>
{%- endmacro -%}

{% macro div(class) -%}
<div class='{{ class | e }}'>
{%- endmacro -%}

{% macro enddiv(class) -%}
</div>
{%- endmacro -%}

{% macro image(filename) -%}
<img src="{{ filename | e }}" class="img-responsive img-thumbnail" style="min-width: 252px;" />
{%- endmacro -%}

{% macro span(class) -%}
<span class='{{ class | e }}'>
{%- endmacro -%}

{% macro endspan(class) -%}
</span>
{%- endmacro -%}

{% macro ul(class) -%}
<ul class="{{ class | e }}">
{%- endmacro -%}

{% macro endul(class) -%}
</ul>
{%- endmacro -%}

{% macro listitem(inner_html, active=false) -%}
<li{% if active != false %} class="active"{% endif %}>{{ inner_html | e }}</li>
{%- endmacro -%}

{% macro br() -%}
<br />
{%- endmacro -%}
