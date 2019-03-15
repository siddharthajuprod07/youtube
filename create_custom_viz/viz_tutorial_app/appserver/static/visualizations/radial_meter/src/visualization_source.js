/*
 * Visualization source
 */
define([
            'jquery',
            'underscore',
            'api/SplunkVisualizationBase',
            'api/SplunkVisualizationUtils',
			'd3'
            // Add required assets to this list
        ],
        function(
            $,
            _,
            SplunkVisualizationBase,
            vizUtils,
			d3
        ) {
  
    // Extend from SplunkVisualizationBase
    return SplunkVisualizationBase.extend({
  
        initialize: function() {
            SplunkVisualizationBase.prototype.initialize.apply(this, arguments);
            this.$el = $(this.el);

            this.$el.append('<h3>This is a custom visualization stand in.</h3>');
            this.$el.append('<p>Edit your custom visualization app to render something here.</p>');
            
            // Initialization logic goes here
			// Add a css selector class
            this.$el.addClass('splunk-radial-meter');
        },

        // Optionally implement to format data returned from search. 
        // The returned object will be passed to updateView as 'data'
        formatData: function(data) {

            // Format data 
			 // Check for an empty data object
		
		//console.log(data);
        if(data.rows.length < 1){
            return false;
        }
		var datum = vizUtils.escapeHtml(parseFloat(data.rows[0][0]));
		//console.log(_.isNaN(datum));
		  // Check for invalid data
    if(_.isNaN(datum)){
		//console.log("Sid");
        throw new SplunkVisualizationBase.VisualizationError(
            'This meter only supports numbers'
        );
    }
     

            return datum;
        },
  
        // Implement updateView to render a visualization.
        //  'data' will be the data object returned from formatData or from the search
        //  'config' will be the configuration property object
        updateView: function(data, config) {
            
            // Draw something here
			//console.log(data);
			 // Return if no data
           if (!data) {
            return;
           }
            // Take the first data point
            datum = data;
			//console.log(datum)
			//console.log(this.$el)
            // Clear the div
            this.$el.empty();
			// Pick a color for now
			//console.log(config);
            var mainColor = config[this.getPropertyNamespaceInfo().propertyNamespace + 'mainColor'] || '#f7bc38';
            // Set domain max
            var maxValue = parseFloat(config[this.getPropertyNamespaceInfo().propertyNamespace + 'maxValue']) || 100;
			// Set height and width
            var height = 220;
            var width = 220;
			// Create a radial scale representing part of a circle
            var scale = d3.scale.linear()
                .domain([0, maxValue])
                .range([ - Math.PI * .75, Math.PI * .75])
                .clamp(true);
				
			// Create parameterized arc definition
            var arc = d3.svg.arc()
                .startAngle(function(d){
                    return scale(0);
                })
                .endAngle(function(d){
                    return scale(d)
                })
                .innerRadius(70)
                .outerRadius(85);
			// SVG setup
            var svg  = d3.select(this.el).append('svg')
                .attr('width', width)
                .attr('height', height)
                .style('background', 'white')
                .append('g')
                .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');
			console.log(arc(100));
			// Background arc
            svg.append('path')
                .datum(maxValue)
                .attr('d', arc)
                .style('fill', 'lightgray');
			// Fill arc
            svg.append('path')
                .datum(datum)
                .attr('d', arc)
                .style('fill', mainColor);
			// Text
            svg.append('text')
                .datum(datum)
                .attr('class', 'meter-center-text')
                .style('text-anchor', 'middle')
                .style('fill', mainColor)
                .text(function(d){
                    return parseFloat(d);
                })
                .attr('transform', 'translate(' + 0 + ',' + 20 + ')');

        },

        // Search data params
        getInitialDataParams: function() {
            return ({
                outputMode: SplunkVisualizationBase.ROW_MAJOR_OUTPUT_MODE,
                count: 10000
            });
        },

        // Override to respond to re-sizing events
        reflow: function() {}
    });
});