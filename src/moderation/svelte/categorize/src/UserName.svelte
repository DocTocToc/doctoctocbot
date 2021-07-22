<script>
   import CreateSocialUser from "./CreateSocialUser.svelte"
    let input = '';
	let screenName = '';
	let apiProtocolDomain = "https://local.doctoctoc.net";
	let apiPath = "/moderation/api/socialuser/";

	let data;
	let socialusers=null;

	function getBaseUrl() {
	    if (window.location.hostname == "localhost") {
	    	return apiProtocolDomain
	    } else {
	    	return ""
	    }
	}	

    async function fetchApi() {
    	let url = getBaseUrl() + apiPath + '?search=' + screenName
    	console.log(url)
	    await fetch(url)
	      .then(r => r.json())
	      .then(data => {
	        //console.log(data);
	        socialusers = data;
	      });
	    return socialusers;
	  };
	  
	async function onClickFetchApi(input) {
		if (input.startsWith('@')) {
		    screenName = input.slice(1);	
		} else {
			screenName = input;
		}
	    socialusers = await fetchApi(screenName)
	    }
</script>


<form action="" method="get" on:submit|preventDefault={onClickFetchApi(input)}>
<label for="screen_name">Enter Twitter screen_name</label>
<input type="text" name="screen_name" id="screen_name" bind:value={input}>
<button type="submit" disabled={!input} on:click={onClickFetchApi(input)}>Fetch!</button>
</form>

  {#key socialusers}
  {#if socialusers && socialusers.length == 0 && screenName}
    <p>Utilisateur inconnu dans notre base de données.</p>
    <CreateSocialUser bind:screenName/>
  {:else if socialusers}
    {#each socialusers as socialuser (socialuser.id) }
    <div class="parent">
    <ul>
    <li><a href="{getBaseUrl()}/admin/moderation/socialuser/{socialuser.id}/change/">🔗 SocialUser admin</a>
    <li>SocialUser id: {socialuser.id}</li>
    <li><a href="https://twitter.com/intent/user?user_id={socialuser.profile.json.id_str}">🔗 Twitter profile</a></li>
    <li>Twitter user id: {socialuser.user_id}</li>
    <li>Twitter screen name: {socialuser.profile.json.screen_name}</li>
    <li>Twitter name: {socialuser.profile.json.name}</li>
    <li>category:
        <div class="parent">
        <ul>
        {#each socialuser.category as cat}
          <li>{cat.label}</li>
        {/each}
        </ul>
        </div>
    </li>
    </ul>
    </div>
    {/each}
  {/if}
  {/key}
	  
<style>
		div.parent {
			text-align: center;
			}
		ul { 
			display: inline-block; 
			text-align: left; 
			}
</style>