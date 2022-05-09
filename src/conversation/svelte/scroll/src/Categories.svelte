<script>
import IconButton, { Icon } from '@smui/icon-button';
import Button, { Label } from '@smui/button';
import {onMount} from "svelte";
import { _ } from "svelte-i18n";
let initialOff = true;
export let id;
export let title;
export let categories = [];
export let selected_categories = [];
let cat_length = 0;
let checkAll = false;
export let query = "";

function arrayRemove(arr, value) {
	return arr.filter(function(ele){ return ele != value; });
}

onMount(() => {
  selected_categories = [];
  query = "";
	})

/*
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
*/
function setAllCheckboxesTo(bool) {
  for (var i = 0; i < categories.length; i++) {
    categories[i].checked = bool;
  }
  selected_categories = [];
  if (bool) {
    for (let category of categories) {
      selected_categories.push(category.taggit_tag)
    }
  }
}

/*
$: if ( selected_categories.length == categories.length && selected_categories.length > 0 ) {
	  checkAll = true;
	}
*/

function checkAllClicked() {
  //console.log(`total: ${categories.length}`);
  //console.log(`selected: ${selected_categories.length}`);
  if ( selected_categories.length == categories.length ) {
	setAllCheckboxesTo(false);
    //console.log(`total: ${categories.length}`);
    //console.log(`selected: ${selected_categories.length}`);
  } else {
	  setAllCheckboxesTo(true);
	  //console.log(`total: ${categories.length}`);
	  //console.log(`selected: ${selected_categories.length}`);
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

  <h4>{title}</h4>
   {#if id=="cat"}
   <div style="display: flex; align-items: center;">
    <IconButton toggle bind:pressed={initialOff} on:click={checkAllClicked}>
      <Icon class="material-icons">star</Icon>
      <Icon class="material-icons" on>star_border</Icon>
    </IconButton>
    <Button on:click={() => (initialOff = !initialOff)} on:click={checkAllClicked}>
      <Label>
        {#if initialOff}
        {$_("select_all")}
        {:else}
        {$_("clear_all")}
        {/if}
      </Label>
    </Button>
  </div>
  {/if}
  <ul>
   {#each categories as category, i}
   <li>
     <div class="custom-control custom-checkbox">
       <input class="custom-control-input" id="customCheck{category.taggit_tag}" type=checkbox bind:group={selected_categories} name="categories" value={category.taggit_tag} bind:checked="{category.checked}">
       <label class="custom-control-label" for="customCheck{category.taggit_tag}">{category.tag}</label>
     </div>
   </li>
   {/each}
   </ul>
<!--p>Selected categories: {selected_categories}</p-->
<!--p>Query:{query}</p-->