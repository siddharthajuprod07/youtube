/**
 * Created by lingda on 7/22/16.
 */
require([
    "splunkjs/mvc",
    "splunk.config",
    "underscore",
    "jquery",
    "splunkjs/mvc/simplexml/ready!"
], function (mvc, splunkConfig, _, $) {
    var service = mvc.createService({"owner": splunkConfig.USERNAME});

    var getUserRolesPromise = function (username) {
        var def = $.Deferred();
        var roles = [];
        var userEndpoint = new splunkjs.Service.Endpoint(service, "authentication/users");
        userEndpoint.get(username, {}, function (err, response) {
            _.each(response.data.entry, function (ent) {
                _.each(ent.content.roles,
                    function (role) {
                        roles.push(role);
                    }
                );
            });
            def.resolve(roles);
        });
        return def;
    };

    var getAllowedIndexesPromise = function (roles) {
        var def = $.Deferred();
        var count = roles.length;
        var allowedIndexes = [];
        var endpoint = new splunkjs.Service.Endpoint(service, "authorization/roles");
        _.each(roles, function (role) {
            endpoint.get(role, {}, function (err, response) {
                _.each(response.data.entry, function (ent) {
                    _.each(_.union(ent.content.imported_srchIndexesAllowed,
                        ent.content.imported_srchIndexesAllowed,
                        ent.content.srchIndexesAllowed,
                        ent.content.srchIndexesDefault),
                        function (index) {
                            allowedIndexes.push(index);
                        }
                    );
                });
                if (--count == 0) {
                    def.resolve(allowedIndexes);
                }
            });
        });
        return def;
    };

    getUserRolesPromise(splunkConfig.USERNAME).then(function (roles) {
        getAllowedIndexesPromise(roles).then(function (allowedIndexes) {
            console.log(allowedIndexes);
            if(!_.contains(allowedIndexes, "_*") && !_.contains(allowedIndexes, "_internal")){
                $('div.dashboard-body').html(
                    '<div class="alert alert-danger perm-error">'+
                        '<i class="icon-alert"></i><strong>Permission denied. You need to have the access to _internal index to view this page.</strong>'+
                    '</div>');
            }
        });
    });


});