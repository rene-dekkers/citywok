function message(){}

generate_message_div = function(message, classes) {
	var $div = $("<div class=\"alert alert-danger alert-dismissible col-md-12\" role=\"alert\"></div>");
	$div.clssName = classes;
	var $button = $("<button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>");
	$div.append($button, $('<strong>Error:</strong>'), ' ' + message);
	$("div[role=\"alert\"]").remove();
	$("#content").prepend($div);
}

message.error = function(message) {
	generate_message_div(message, "alert alert-danger alert-dismissible");
}

$(document).ready(function(){
	$('[title]').tooltip(); 

	$(".clearsearch").click(function(){
		if ($("#searchinput").val() != '') {
			$("#searchinput").val('');
			$("#searchform").submit();
		}
	});

});

function update_state(virtual, state) {
	$.ajax({
		type: 'PUT', // Use POST with X-HTTP-Method-Override or a straight PUT if appropriate.
		dataType: 'json', // Set datatype - affects Accept header
		url: "/virtual/" + virtual + "/state",
		contentType: "application/json",
		data: JSON.stringify({ state: state })
	}).done(function(data) {
		if (state == 'running') {
			location.reload();
		}
	}).fail(function(data) {
		message.error(data.responseJSON['message']);
        });
;
}
