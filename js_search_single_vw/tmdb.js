require([
	'splunkjs/mvc/searchmanager',
	'splunkjs/mvc/postprocessmanager',
	'splunkjs/mvc/singleview',
    "splunkjs/mvc/simplexml/ready!"
], function(SearchManager,PostProcessManager,SingleView) { 

	new SearchManager({
		id: "base_search",
		earliest_time: "0",
		latest_time: "now",
		preview: true,
		cache: false,
		search: "index=\"tmdb_index\" | table id,release_date,title,genre_ids{},original_language,original_title,overview,popularity | mvexpand genre_ids{} | rename genre_ids{} as genre_id | eval release_date_epoc = strptime(release_date,\"%Y-%m-%d\") | eval release_year = strftime(release_date_epoc,\"%Y\") | fillnull value=\"Not Defined\" release_year,genre_id,original_language" 
	});

	var single_pnl_post_srch = new PostProcessManager({
		id: "single_panel_srch",
		managerid: "base_search",
		search: "| dedup id | stats count" 
	});

	single_pnl_post_srch.on('search:done',function(properties){
		var myResults = single_pnl_post_srch.data('results');
		myResults.on('data',function(){
			console.log(myResults.hasData())
			console.log(myResults.data().rows[0][0])
			console.log(myResults.collection().raw.rows[0][0])
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


});