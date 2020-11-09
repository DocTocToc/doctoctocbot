<script>
  import {onMount} from "svelte";
  import { _, getLocaleFromNavigator } from "svelte-i18n";
  import dayjs from 'dayjs';
  import customParseFormat from  'dayjs/plugin/customParseFormat';
  dayjs.extend(customParseFormat)
  import relativeTime from 'dayjs/plugin/relativeTime';
  dayjs.extend(relativeTime);
  import localizedFormat from 'dayjs/plugin/localizedFormat';
  dayjs.extend(localizedFormat)
  import 'dayjs/locale/en'
  import 'dayjs/locale/fr'
  import Images from "./Images.svelte";

  
  // we need to remove "-FR" from "fr-FR"
  function setDayjsLocale() {
	var extLocale = getLocaleFromNavigator(); 
    var locale = extLocale.substring(0, extLocale.indexOf("-"));
    dayjs.locale(locale); // use loaded locale globally
  }
  export let baseURL;
  export let status;
  export let has_status_category;
  export let has_status_tag;
  
  onMount(()=> {
    setDayjsLocale();
  })  
  
  function dateTimeLocale(id_str) {
	    var datetime = dateTime(id_str);
	    return dayjs(datetime).format('llll')
	  }
  
  function dateTime(id_str) {
	let status_id = BigInt(id_str);
	let offset = BigInt(1288834974657);
	let timestamp = ((status_id >> BigInt(22)) + offset);
	var created_at = new Date(Number(timestamp));
    return created_at;
  }
  function fromNow(id_str) {
	let dt = dateTime(id_str);
    let dtFromNow = dayjs(dt).locale(getLocaleFromNavigator()).fromNow();
    return dtFromNow;
  }
  function categoryOrTag(status) {
	  if ( status.status_tag == null && status.status_category == null ) {
		  return false
	  }
	  if (status.status_tag.length == 0 && status.status_category.length == 0) {
		  return false
	  } else {
		  return true
	  }
  }
</script>

<style>

.Icon {
    display: inline-block;
    height: 1.25em;
    background-repeat: no-repeat;
    background-size: contain;
    vertical-align: text-bottom
}

.Icon--twitter {
    width: 1.25em;
    background-image:
        url("data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2072%2072%22%3E%3Cpath%20fill%3D%22none%22%20d%3D%22M0%200h72v72H0z%22%2F%3E%3Cpath%20class%3D%22icon%22%20fill%3D%22%231da1f2%22%20d%3D%22M68.812%2015.14c-2.348%201.04-4.87%201.744-7.52%202.06%202.704-1.62%204.78-4.186%205.757-7.243-2.53%201.5-5.33%202.592-8.314%203.176C56.35%2010.59%2052.948%209%2049.182%209c-7.23%200-13.092%205.86-13.092%2013.093%200%201.026.118%202.02.338%202.98C25.543%2024.527%2015.9%2019.318%209.44%2011.396c-1.125%201.936-1.77%204.184-1.77%206.58%200%204.543%202.312%208.552%205.824%2010.9-2.146-.07-4.165-.658-5.93-1.64-.002.056-.002.11-.002.163%200%206.345%204.513%2011.638%2010.504%2012.84-1.1.298-2.256.457-3.45.457-.845%200-1.666-.078-2.464-.23%201.667%205.2%206.5%208.985%2012.23%209.09-4.482%203.51-10.13%205.605-16.26%205.605-1.055%200-2.096-.06-3.122-.184%205.794%203.717%2012.676%205.882%2020.067%205.882%2024.083%200%2037.25-19.95%2037.25-37.25%200-.565-.013-1.133-.038-1.693%202.558-1.847%204.778-4.15%206.532-6.774z%22%2F%3E%3C%2Fsvg%3E")
}

.name {
    font-weight: bold;
}

.screen_name {
    font-weight: normal;
    color: grey;
}

.profile-pic {
    width: 49px;
}
</style>

<div class="card">
    <div class="card-body">
      <div>
        <img class="rounded-circle profile-pic float-left pr-1" src="{baseURL}{status.avatar_normal}" alt="Profile pic">
        <h6 class="card-title">
          <span class="name mx-1">{status.user_name}</span><span class="screen_name mx-1">@{status.user_screen_name}</span>
        </h6>
      </div>
      <h6 class="card-subtitle mb-2 text-muted">
      {#if status.author_category}
      <span class="badge badge-primary">{status.author_category}</span>
      {/if}
      {#if status.author_specialty}
      <span class="badge badge-secondary">{status.author_specialty}</span>
      {/if}
      </h6>
      <p class="card-text">{status.text}</p>
      {#if categoryOrTag(status) }
      <div class="mx-0 mt-0 mb-1">
        {#if has_status_category}
        {#each status.status_category as category}
        <span class="badge badge-pill badge-info mx-1">{category}</span>
        {/each}
        {/if}
        {#if has_status_tag}
        {#each status.status_tag as tag}
        <span class="badge badge-pill badge-dark mx-1">{tag}</span>
        {/each}
        {/if}
      </div>
      {/if}
      <Images
        images={status.media} />
      <div class="card-footer">
        <span class="card-text" data-toggle="tooltip" title="{dateTimeLocale(status.id_str)}">
        {fromNow(status.id_str)}
        </span>
        <span><a href="https://twitter.com/{status.user_screen_name}/status/{status.id_str}" class="card-link" aria-label={$_("view_on_twitter")}>
        {$_("view_on_twitter")}
        <div class="Icon Icon--twitter" title={$_("view_on_twitter")}></div>
        </a>
        </span>
      </div>


    </div>
</div>