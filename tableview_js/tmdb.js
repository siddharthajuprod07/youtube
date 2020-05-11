require([
	'splunkjs/mvc/searchmanager',
	'splunkjs/mvc/postprocessmanager',
	'splunkjs/mvc/singleview',
    'splunkjs/mvc/chartview',
    'splunkjs/mvc/tableview',
    'underscore',
    "splunkjs/mvc/simplexml/ready!"
], function(SearchManager,PostProcessManager,SingleView,ChartView,TableView,_) { 

	new SearchManager({
		id: "base_search",
		earliest_time: "0",
		latest_time: "now",
		preview: true,
		cache: false,
		search: "index=\"tmdb_index\" | table id,release_date,title,genre_ids{},original_language,original_title,overview,popularity,backdrop_path | mvexpand genre_ids{} | rename genre_ids{} as genre_id | eval release_date_epoc = strptime(release_date,\"%Y-%m-%d\") | eval release_year = strftime(release_date_epoc,\"%Y\") | fillnull value=\"Not Defined\" release_year,genre_id,original_language" 
	});

	var single_pnl_post_srch = new PostProcessManager({
		id: "single_panel_srch",
		managerid: "base_search",
		search: "| dedup id | stats count" 
	});

	single_pnl_post_srch.on('search:done',function(properties){
		var myResults = single_pnl_post_srch.data('results');
		myResults.on('data',function(){
			//console.log(myResults.hasData())
			//console.log(myResults.data().rows[0][0])
			//console.log(myResults.collection().raw.rows[0][0])
		})
	});

	new SingleView({
		id: "single_view_count",
		colorMode:"block",
		underLabel: "Total Movies",
		rangeColors : '["0x53a051","0x0877a6","0xf8be34","0xf1813f","0x006d9c"]',
		rangeValues : '[0,30,70,100]',
		useColors : 'true',
		managerid: "single_panel_srch",
		el: $("#total_movie_count")
	}).render();

	var pie_chart_post_srch = new PostProcessManager({
		id: "pie_chart_srch",
		managerid: "base_search",
		search: "| dedup id | stats count by release_year" 
	});

	var piechart = new ChartView({
        id: "example-pie-chart",
        managerid: "pie_chart_srch",
        type: "pie",
        el: $("#year_wise_breakup")
	}).render();

	
	var bar_chart_post_srch = new PostProcessManager({
		id: "bar_chart_srch",
		managerid: "base_search",
		search: "| dedup id | stats count by original_language" 
	});

	var barchart = new ChartView({
        id: "example-bar-chart",
		managerid: "bar_chart_srch",
		drilldownRedirect : "false",
        type: "bar",
        el: $("#lang_wise_breakup")
	}).render();

	barchart.settings.set( "charting.chart.barSpacing", "5" )

	barchart.on("click:chart", function (e) {
        e.preventDefault(); // Prevent redirecting to the Search app
		console.log("Clicked chart: ", e); // Print event info to the console
		console.log("Clicked chart: ", e.name);
	});
	

	var line_chart_post_srch = new PostProcessManager({
		id: "line_chart_srch",
		managerid: "base_search",
		search: "| dedup id | stats count by genre_id" 
	});

	var linechart = new ChartView({
        id: "example-line-chart",
		managerid: "line_chart_srch",
		//resizable : "true",
		//height : "750",
        type: "line",
        el: $("#genre_wise_breakup")
	}).render();

	linechart.on("click:legend", function (e) {
        e.preventDefault(); // Prevent redirecting to the Search app
		console.log("Clicked legend: ", e); // Print event info to the console
    });

    var movie_dtl_srch = new PostProcessManager({
		id: "tbl_srch",
		managerid: "base_search",
		search: "| dedup id | table release_date,title,popularity,backdrop_path,overview | where backdrop_path != \"null\"" 
	});

    var myCustomtable = new TableView({
        id: "example-table",
        managerid: "tbl_srch",
        pageSize: "10",
        el: $("#movie_dtl")
    }).render();

    var movie_title=""
    var popularity = ""
    var release_date = ""
    // Inherit from the BaseCellRenderer base class
    var MyCustomCellRenderer = TableView.BaseCellRenderer.extend({
        initialize: function() {
           //
        },
        canRender: function(cellData) {
            // Required
            return cellData.field === "release_date" || cellData.field === "title" || cellData.field === "overview" || cellData.field === "popularity" || cellData.field === "backdrop_path"
           
        },
        setup: function($td, cellData) {
            //
        },
        teardown: function($td, cellData) {
            //
        },
        render: function($td, cellData) {
            // Required
            if (cellData.field === "title") {
                movie_title = cellData.value
            }
            if (cellData.field === "popularity") {
                popularity = cellData.value
            }
            if (cellData.field === "release_date") {
                release_date = cellData.value
            }
            var image_url = "https://image.tmdb.org/t/p/w500" + cellData.value
            if (cellData.field === "backdrop_path") {
                $td.addClass('some_class').html(_.template(
                    `<img src="<%-image_url%>"></img>
                    <h2>Movie Title : <%-title%></h2>
                    <h2>Popularity :<%-popularity%></h2>
                    <h2>Release Date : <%-release_date%></h2>`
                ,{image_url:image_url,title:movie_title,popularity:popularity,release_date:release_date}))
            }
            if (cellData.field === "overview") {
                $td.addClass('some_class1').html(_.template(
                    `<p align=left><%-overview%></p>`
                    ,{overview:cellData.value}
                ))
            }
        }
    });

    var myCellRenderer = new MyCustomCellRenderer();

    myCustomtable.addCellRenderer(myCellRenderer); 

    myCustomtable.render();

});