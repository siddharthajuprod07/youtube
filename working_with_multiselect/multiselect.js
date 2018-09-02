require([
'jquery',
'underscore',
'splunkjs/mvc',
'splunkjs/mvc/simplexml/ready!'
],
function($,_,mvc){
	var multi1 = mvc.Components.get("multi1")
	multi1.on("change",function(){
		current_val = multi1.val()
		console.log("Current Vals: " + current_val)
		var first_choice_value = multi1.options.choices[0].value;
		if (current_val.length > 1 && current_val.indexOf(first_choice_value) == 0) {
			multi1.val(_.without(current_val, first_choice_value));
		}
		if (current_val.length > 1 && current_val.indexOf(first_choice_value) > 0) {
			multi1.val([first_choice_value]);
		}
	})
}
)