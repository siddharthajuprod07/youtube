 require(['jquery', 'underscore', 'splunkjs/mvc'], function($, _, mvc) {
    function setToken(name, value) {
        //console.log('Setting Token %o=%o', name, value);
        var defaultTokenModel = mvc.Components.get('default');
        if (defaultTokenModel) {
            defaultTokenModel.set(name, value);
        }
        var submittedTokenModel = mvc.Components.get('submitted');
        if (submittedTokenModel) {
            submittedTokenModel.set(name, value);
        }
    }	  
	  $('.dashboard-body').on('click','[data-set-token],[data-unset-token],[data-token-json]', function(e) {
		  console.log(e)
		  e.preventDefault();
		  var target = $(e.currentTarget);
		  var setTokenName = target.data('set-token');
		  console.log(setTokenName)
        if (setTokenName) {
            setToken(setTokenName, target.data('value'));
        }
        var unsetTokenName = target.data('unset-token');
        if (unsetTokenName) {
            setToken(unsetTokenName, undefined);
        }
	  }
 )});