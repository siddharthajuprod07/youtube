require([
	'splunkjs/mvc/searchmanager',
	'splunkjs/mvc/postprocessmanager',
	'splunkjs/mvc/singleview',
    'splunkjs/mvc/chartview',
    'splunkjs/mvc/tableview',
    'underscore',
    'splunkjs/mvc/multidropdownview',
    'splunkjs/mvc/dropdownview',
    'splunkjs/mvc',
    "splunkjs/mvc/simplexml/ready!"
], function(SearchManager,
    PostProcessManager,
    SingleView,
    ChartView,
    TableView,
    _,
    MultiDropdownView,
    DropdownView,
    mvc) { 

	new SearchManager({
		id: "base_search",
		earliest_time: "0",
		latest_time: "now",
		preview: true,
		cache: false,
		search: "index=\"tmdb_index\" | table id,release_date,title,genre_ids{},original_language,original_title,overview,popularity,backdrop_path | mvexpand genre_ids{} | rename genre_ids{} as genre_id | eval release_date_epoc = strptime(release_date,\"%Y-%m-%d\") | eval release_year = strftime(release_date_epoc,\"%Y\") | fillnull value=\"Not Defined\" release_year,genre_id,original_language"
    });

    var rlse_yr_post_srch = new PostProcessManager({
		id: "rlse_yr_md_srch",
		managerid: "base_search",
		search: "| stats count by release_year" 
    });
    
    var mychoices = [
        {label:"All", value: "*"}
    ];
    
    new MultiDropdownView({
        id: "release-year-multidropdown",
        managerid: "rlse_yr_md_srch",
        choices: mychoices,
        default: "*",
        value: mvc.tokenSafe("$release_year$"),
        labelField: "release_year",
        valueField: "release_year",
        el: $("#release_year_md")
    }).render();

    var multi1 = mvc.Components.get("release-year-multidropdown")
    var defaultTokenModel = mvc.Components.get("default")
    defaultTokenModel.set("release_yr_transfored","*")
	multi1.on("change",function(){
		var current_val = multi1.val()
		//console.log(current_val)
		var first_choice_val = multi1.options.choices[0].value;
		if (current_val.length > 1 && current_val.indexOf(first_choice_val) == 0) {
			multi1.val(_.without(current_val,first_choice_val))
		}
		if (current_val.length > 1 && current_val.indexOf(first_choice_val) > 0) {
			multi1.val(first_choice_val)
        }
        var modifed_val = multi1.val()
        var trnsformed_release_yr = ""
        console.log(modifed_val)
        $.each(modifed_val,function(index,item){
            trnsformed_release_yr = trnsformed_release_yr + 'release_year="' + item + '"' + " OR "
        })
        
        var release_yr_token_val = trnsformed_release_yr.substr(0,trnsformed_release_yr.lastIndexOf("OR")-1)
        console.log(release_yr_token_val)
        defaultTokenModel.set("release_yr_transfored",release_yr_token_val)
	}
	)


    var genre_id_post_srch = new PostProcessManager({
		id: "genre_id_dd_srch",
		managerid: "base_search",
		search: "| stats count by genre_id" 
    });

    new DropdownView({
        id: "genre-id-dropdown",
        managerid: "genre_id_dd_srch",
        choices: mychoices,
        default: "*",
        value: mvc.tokenSafe("$genre_id$"),
        labelField: "genre_id",
        valueField: "genre_id",
        el: $("#genre_id_dd")
    }).render();

    var orig_lang_post_srch = new PostProcessManager({
		id: "orig_lang_dd_srch",
		managerid: "base_search",
		search: "| stats count by original_language" 
    });

    new DropdownView({
        id: "orig_lang-dropdown",
        managerid: "orig_lang_dd_srch",
        choices: mychoices,
        default: "*",
        value: mvc.tokenSafe("$orig_ln$"),
        labelField: "original_language",
        valueField: "original_language",
        el: $("#orig_lang_dd")
    }).render();

	var single_pnl_post_srch = new PostProcessManager({
		id: "single_panel_srch",
		managerid: "base_search",
		search: "| search $release_yr_transfored$ genre_id=$genre_id$ original_language=$orig_ln$ | dedup id | stats count" 
	}, {tokens: true});

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
		search: "| search $release_yr_transfored$ genre_id=$genre_id$ original_language=$orig_ln$| dedup id | stats count by release_year"
	}, {tokens: true});

	var piechart = new ChartView({
        id: "example-pie-chart",
        managerid: "pie_chart_srch",
        type: "pie",
        el: $("#year_wise_breakup")
	}).render();

	
	var bar_chart_post_srch = new PostProcessManager({
		id: "bar_chart_srch",
		managerid: "base_search",
		search: "| search $release_yr_transfored$ genre_id=$genre_id$ original_language=$orig_ln$| dedup id | stats count by original_language" 
	}, {tokens: true});

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
		search: "| search $release_yr_transfored$ genre_id=$genre_id$ original_language=$orig_ln$| dedup id | stats count by genre_id"
	}, {tokens: true});

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
		search: "| search $release_yr_transfored$ genre_id=$genre_id$ original_language=$orig_ln$| dedup id | table release_date,title,popularity,backdrop_path,overview | where backdrop_path != \"null\"" 
	}, {tokens: true});

    var myCustomtable = new TableView({
        id: "example-table",
        managerid: "tbl_srch",
        pageSize: "10",
        el: $("#movie_dtl")
    }).render();

    var movie_title=""
    var popularity = ""
    var release_date = ""
    var base_url = ""
    var poster_size = ""
    $.ajax({ 
        type: "GET",
        dataType: "json",
        data: {api_key: '733ac994290c6f277b11565f26ebe1cb' },
        url: "https://api.themoviedb.org/3/configuration",
        success: function(data){        
           base_url = data["images"]["secure_base_url"];
           poster_size = data["images"]["backdrop_sizes"][1]
           //console.log(base_url)
           //console.log(poster_size)
        }
    });
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
            
            if (cellData.field === "backdrop_path") {
                //var image_url = "https://image.tmdb.org/t/p/w500" + cellData.value
                var image_url = base_url + "/" + poster_size + cellData.value
                $td.addClass('some_class').html(_.template(
                    `<img src="<%-image_url%>"></img>
                    <h1>Movie Title : <%-title%></h1>
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