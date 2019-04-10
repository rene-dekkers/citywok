<div class='col-sm-offset-3 col-sm-6'>
	<center>
		<h1>{% if header_name %}{{ header_name }}{% else %}CityWok{% endif %}</h1>
		<p class='light'>
		{% if welcome_msg %}
			{% autoescape false %}{{ welcome_msg }}{% endautoescape %}
		{% else %}  
			<a href="https://git.better-it-solutions.nl/virtualization/citywok" target="_blank">CityWok</a>
			{% trans %}version{% endtrans %}&nbsp;{{ g.version }}
		{% endif %}
		</p>
	</center>
</div>
