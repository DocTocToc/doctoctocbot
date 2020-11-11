<script>
	import {onMount} from "svelte";
	import { addMessages, init, _, getLocaleFromNavigator } from "svelte-i18n";
	import InfiniteScroll from "./InfiniteScroll.svelte";
	import Status from "./Status.svelte";
	import Categories from "./Categories.svelte";
    import DatePicker from "./DatePicker.svelte";
    import en from "../public/lang/en.json";
    import fr from "../public/lang/fr.json";

    addMessages("en", en);
    addMessages("fr", fr);

    init({
      initialLocale: "fr",
      initialLocale: getLocaleFromNavigator(),
    });
    let baseURL = "";
	//let baseURL="http://local.doctoctoc.net";
	// if the api (like in this example) just have a simple numeric pagination
    let page = 1;
	// but most likely, you'll have to store a token to fetch the next page
	let nextUrl = null;
	// tweets json response
	let resTweets = '';
    // categories json response
    let resCategories = '';
    let resTags = '';
    // store all the data here.
	let data = [];
	// store the new batch of data here.
	let newBatch = [];
	// store categories there
	let categories = [];
	// store tags there
	let tags = [];
	// not categorized
	let not_categorized = {
	  tag: $_("uncategorized"),
	  summary: $_("uncategorized_summary"),
	  taggit_tag: 0,
	  checked: true,
	}
	let selected_categories = [];
	let selected_tags = [];
	let cat_query = "";
	let tag_query = "";
	const initialUrl = `${baseURL}/conversation/api/v1/tweets/?format=json&page=1`;
	let hasMore = false;
	
	let api_access;
	let has_search_datetime = false;
	let has_search_category = false;
	let has_search_tag = false;
	let has_status_category = false;
	let has_status_tag = false;
	
	// Error handling
	function errorResponse(code, msg) {
	    return e => {
	        e.status = code;
	        e.details = msg;
	        throw e;
	    };
	}
	function ifEmpty(fn) {
	    return o => o || fn(new Error("empty"));
	}

	/* DatePickr */
	let from_datetime_query = "";
	let to_datetime_query = "";
		
	async function fetchDataTweets() {
	    let data_url = (nextUrl == null) ? initialUrl : nextUrl;
	    if ( data_url == "null" ) {
	    	return;
	    }
	    //console.log(`fetching: ${data_url}${cat_query}${tag_query}`)
		const response = await fetch(`${data_url}${cat_query}${tag_query}${from_datetime_query}${to_datetime_query}`);
		resTweets = await response.json();
		//console.log(resTweets);
		newBatch = resTweets["results"];
        //console.log(newBatch);
        nextUrl = resTweets["next"];
        //console.log(`nextUrl: ${nextUrl}`);
        hasMore = (nextUrl == null) ? false : true;
	};

    async function fetchDataCategories() {
        const response = await fetch(`${baseURL}/tagging/api/v1/categories/`);
        if (!response.ok) {
          	const message = `An error has occured: ${response.status}`;
           	//console.log(message);
           	return
        }
        resCategories =  await response.json();
        categories = resCategories["results"];
        for (var i = 0; i < categories.length; i++) {
            categories[i].checked = true;
            selected_categories.push(categories[i].taggit_tag);
        }
        categories.push(not_categorized)
        selected_categories.push(not_categorized.taggit_tag);
    };

    async function fetchDataTags() {
        const response = await fetch(`${baseURL}/tagging/api/v1/tags/`);
        if (!response.ok) {
          	const message = `An error has occured: ${response.status}`;
           	//console.log(message);
           	return
        }
        resTags = await response.json();
        tags = resTags["results"];
        for (var i = 0; i < tags.length; i++) {
            tags[i].checked = false;
            tags[i]["taggit_tag"] = tags[i].tag.toString();
            tags[i]["tag"] = tags[i].tag_name;
        }                 
    };

    async function fetchUserApiAccess() {
        const response = await fetch(`${baseURL}/community/api/v1/user-api-access/`);
        if (!response.ok) {
          	const message = `An error has occured: ${response.status}`;
           	//console.log(message);
           	return
        }
        api_access = await response.json();
        //console.log(api_access);
    	has_search_datetime = api_access["search_datetime"];
    	has_search_category = api_access["search_category"];
    	has_search_tag = api_access["search_tag"];
    	has_status_category = api_access["status_category"];
    	has_status_tag = api_access["status_tag"];
    };

	onMount(()=> {
		fetchUserApiAccess();
		// load first batch
		fetchDataTweets();
		// load categories
		fetchDataCategories();
		// load tags
		fetchDataTags();
	})

  $: data = [
		...data,
    ...newBatch
  ];
	
  $: if ( cat_query.length > 0 ) {
    data = [];
    newBatch = [];
    nextUrl = null;
    fetchDataTweets();
  };
    
  $: if ( tag_query.length > 0 ) {
    data = [];
    newBatch = [];
    nextUrl = null;
    fetchDataTweets();
  };
  
  $: if ( from_datetime_query.length > 0 ) {
    data = [];
    newBatch = [];
    nextUrl = null;
    fetchDataTweets();
  };

  $: if ( to_datetime_query.length > 0 ) {
	data = [];
	newBatch = [];
	nextUrl = null;
	fetchDataTweets();
  };

</script>

<style>
  main {
    display: flex;
    width: 100%;
    height: 100%;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }

  ul {
    box-shadow: 0px 1px 3px 0px rgba(0, 0, 0, 0.2),
      0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 2px 1px -1px rgba(0, 0, 0, 0.12);
    display: flex;
    flex-direction: column;
    border-radius: 2px;
    width: 100%;
    max-width: 800px;
    max-height: 800px;
    background-color: white;
    overflow-x: scroll;
    list-style: none;
    padding: 0;
  }

  li {
    padding: 15px;
    box-sizing: border-box;
    transition: 0.2s all;
    font-size: 14px;
  }

  li:hover {
    background-color: #eeeeee;
  }
  
  .scroll-footer {
    font-size: smaller;
  }
</style>



<div class="container">
  <div class="row">
    <div class="col-md-auto">
      {#if has_search_category}
      <Categories
        bind:categories
        bind:selected_categories
        bind:query={cat_query}
        title={$_("status_categories")}
        id={"cat"}/>
      {/if}
      {#if has_search_tag}
      <Categories
        categories={tags}
        bind:selected_categories={selected_tags}
        bind:query={tag_query}
        title={$_("status_tags")}
        id={"tag"}/>
      {/if}
      {#if has_search_datetime}
        <DatePicker
          bind:from_datetime_query
          bind:to_datetime_query/>
      {/if}
    </div>

    <div class="col">
      <ul class="list-group my-1">
        {#each data as item}
        <li class="list-group-item">
          <Status
            status={item}
            baseURL={baseURL}
            bind:has_status_category
            bind:has_status_tag />
        </li>
        {/each}
        <InfiniteScroll
          bind:hasMore
          threshold=0
          on:loadMore={() => {fetchDataTweets();}} />
      </ul>
      <p class="scroll-footer">
      {#if data.length}
        {hasMore ? $_('all_items_loaded_no') : $_('all_items_loaded_yes')}
      {:else}
        {$_('no_item_found')}
      {/if}
      </p>
    </div>
  </div>
</div>