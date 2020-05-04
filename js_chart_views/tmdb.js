require([
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
	"splunkjs/mvc/singleview",
	"splunkjs/mvc/chartview",
    "splunkjs/mvc/simplexml/ready!"
], function(SearchManager,
    PostProcessManager,
	SingleView,
	ChartView) { 
    var mybaseSearch = new SearchManager({
        id: "base_search",
        earliest_time: "0",
        latest_time: "now",
        preview: true,
        cache: false,
        search: "index=tmdb_index | table id,release_date,title,genre_ids{},original_language,original_title,overview,popularity | mvexpand genre_ids{} | rename genre_ids{} as genre_id | eval release_date_epoc = strptime(release_date,\"%Y-%m-%d\") | eval release_year = strftime(release_date_epoc,\"%Y\") | fillnull value=\"Not Defined\" release_year,genre_id,original_language" 
    });

    var single_panel_search = new PostProcessManager({
        id: "single_panel",
        managerid: "base_search",
        search: "| dedup id | stats count" 
    });

    single_panel_search.on('search:done',function(properties){
        //do something
        var myResults = single_panel_search.data('results');
        //console.log(myResults)
        myResults.on("data", function() {
            console.log(myResults.hasData())
            console.log(myResults.data().rows)
            console.log(myResults.data().rows[0][0])
            console.log(myResults.collection().raw.rows)
        });
    });

    new SingleView({
        id: "movie_count",
        managerid: "single_panel",
        colorMode : "block",
        rangeColors : '["0x53a051","0x0877a6","0xf8be34","0xf1813f","0x006d9c"]',
        rangeValues : '[0,30,70,100]',
        underLabel : "Total Movies",
        useColors : "true",
        el: $("#movie_count")
	}).render();
	
	var pie_chart_search = new PostProcessManager({
        id: "pie-chart",
        managerid: "base_search",
        search: "| dedup id | stats count  by release_year" 
    });

	var piechart = new ChartView({
        id: "example-pie-chart",
        managerid: "pie-chart",
        type: "pie",
        el: $("#year_wise_brkup")
	}).render();

	var bar_chart_search = new PostProcessManager({
        id: "bar-chart",
        managerid: "base_search",
        search: "| dedup id | stats count  by original_language" 
	});
	
	var barchart = new ChartView({
        id: "example-bar-chart",
        managerid: "bar-chart",
        type: "bar",
        el: $("#lang_wise_brkup")
	}).render();

	barchart.settings.set( "charting.chart.barSpacing", "5" )

	barchart.on("click:chart", function (e) {
        e.preventDefault(); // Prevent redirecting to the Search app
        console.log("Clicked chart: ", e.name); // Print event info to the console
    });

	var line_chart_search = new PostProcessManager({
        id: "line-chart",
        managerid: "base_search",
        search: "| dedup id | stats count  by genre_id" 
	});

	var linechart = new ChartView({
        id: "example-line-chart",
        managerid: "line-chart",
        type: "line",
        el: $("#genre_wise_brkup")
	}).render();

	linechart.on("click:legend", function (e) {
        e.preventDefault(); // Prevent redirecting to the Search app
        console.log("Clicked chart: ", e); // Print event info to the console
    });
 });