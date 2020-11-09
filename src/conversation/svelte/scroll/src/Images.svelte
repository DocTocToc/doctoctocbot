<script>
  import {onMount} from "svelte";

  export let images;
  let urls = [];
  
  function get_thumbs(entities) {
	  if ( entities == null ) {
		  return
	  }
	  let thumbs = [];
	  var entity;
	  for (entity of entities) {
		  let media_url_https = entity["media_url_https"];
			let last_dot_idx = media_url_https.lastIndexOf(".");
			let base_url_https = media_url_https.substring(0, last_dot_idx);
			let format = media_url_https.substring(last_dot_idx + 1);
			let thumb = base_url_https + "?format=" + format + "&name="
			thumbs.push(thumb);
	  }
	  return thumbs
  }
	
  onMount(()=> {
		if ( images ) {
		  urls = get_thumbs(images);
		}
  })
</script>

<style>

</style>

{#each urls as url}
<a href="{url}large">
<img src="{url}thumb" class="img-fluid" alt="tweet image">
</a>
{/each}