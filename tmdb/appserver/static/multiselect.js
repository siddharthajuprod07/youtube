require([
'jquery',
'underscore',
'splunkjs/mvc',
'splunkjs/mvc/simplexml/ready!'
],
function($,_,mvc){
	var multi1 = mvc.Components.get("multi1")
	multi1.on("change",function(){
		var current_val = multi1.val()
		console.log(current_val)
		var first_choice_val = multi1.options.choices[0].value;
		if (current_val.length > 1 && current_val.indexOf(first_choice_val) == 0) {
			multi1.val(_.without(current_val,first_choice_val))
		}
		if (current_val.length > 1 && current_val.indexOf(first_choice_val) > 0) {
			multi1.val(first_choice_val)
		}
	}
	)
}
)