<script>

import {onMount} from "svelte";
import { _ } from "svelte-i18n";
export let id;
export let title;
export let categories = [];
export let selected_categories;
let cat_length = 0;
let checkAll = true;
export let query = "";

function arrayRemove(arr, value) {
	return arr.filter(function(ele){ return ele != value; });
}

function addCheckedToSelected(bool) {
  for (var i = 0; i < categories.length; i++) {
	categories[i].checked = bool;
   	let tagit = categories[i].taggit_tag;
  	if ( selected_categories.includes(tagit) == false && bool ) { 
   	  selected_categories.push(tagit)
    } else if ( selected_categories.includes(tagit) == true && bool == false ) {
      selected_categories = arrayRemove(selected_categories, tagit);
    }
  }
}

function setAllCheckboxesTo(bool) {
  for (var i = 0; i < categories.length; i++) {
    categories[i].checked = bool;	
  }
  addCheckedToSelected(bool)
}

function checkedCount() {
  let count = 0;
  for (var i = 0; i < categories.length; i++) {
    if (categories[i].checked === true) {
      count += 1; 
    }
  }
  return count;
}

$: if ( selected_categories.length == categories.length ) {
	  checkAll = true;
	}

$: if ( selected_categories.length < categories.length ) {
  checkAll = false;
}

function checkAllClicked() {
  //console.log(`total: ${categories.length}`);
  //console.log(`selected: ${selected_categories.length}`);
  if ( selected_categories.length < categories.length ) {
	setAllCheckboxesTo(true);
    //console.log(`total: ${categories.length}`);
    //console.log(`selected: ${selected_categories.length}`);
	checkAll=true;
  } else if ( selected_categories.length == categories.length ) {
	if  (selected_categories.length == 0) {
	  setAllCheckboxesTo(true);
	  //console.log(`total: ${categories.length}`);
	  //console.log(`selected: ${selected_categories.length}`);
	} else {
	  setAllCheckboxesTo(false);
	  //console.log(`total: ${categories.length}`);
	  //console.log(`selected: ${selected_categories.length}`);
	}
  }
}

function buildQuery() {
	let q = "&";
	for(let i = 0; i < selected_categories.length; i++) {
		q = q+`tag=${selected_categories[i]}`;
		if ( i < (selected_categories.length - 1) ) {
			q = q+"&"
		}
	}
	//console.log(`query: ${q}`);
	return q;
}

$: if ( selected_categories.length > 0 ) {
	query = buildQuery();
} else {
	query=""
}

</script>
 
<style>
ul {
	  column-count: 2;
	  column-gap: 1rem;
	  list-style: none;
	}
</style>

  <h3>{title}</h3>
   <ul>
   {#if id=="cat"}
   <li>
   <div class="custom-control custom-checkbox">
     <input class="custom-control-input" id="checkAll{id}" type="checkbox" bind:checked="{checkAll}" on:click="{checkAllClicked}">
     <label class="custom-control-label font-weight-bold" for="checkAll{id}"><bold>{$_("select_all")}</bold></label>
   </div>
   </li>
   {/if}
   {#each categories as category, i}
   <li>
     <div class="custom-control custom-checkbox">
       <input class="custom-control-input" id="customCheck{category.taggit_tag}" type="checkbox" bind:group={selected_categories} value="{category.taggit_tag}" bind:checked="{category.checked}">
       <label class="custom-control-label" for="customCheck{category.taggit_tag}">{category.tag}</label>
     </div>
   </li>
   {/each}
   </ul>
<!--p>Selected categories: {selected_categories}</p-->
<!--p>Query:{query}</p-->