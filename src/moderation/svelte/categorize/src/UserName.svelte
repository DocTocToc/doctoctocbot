<script>
    import { onMount } from 'svelte';
    import CreateSocialUser from "./CreateSocialUser.svelte"
    import HealthCareProvider from "./HealthCareProvider.svelte"
    let input = '';
	let screenName = '';
	let apiPath = "/moderation/api/socialuser/";
	let screenNameValue = '';
	let socialusers=null;
	let humanId=0;

	$: {
		let param = (new URL(document.location)).searchParams.get('screen_name');
		if ( param ) {
			console.log(param);
			socialusers = fetchApi(param);
			screenName = param;
			input = param;
		}
	}
	
	function getScreenNameValue() {
		return (new URL(document.location)).searchParams.get('screen_name')
	}
	

    async function fetchApi(sn) {
    	let url = apiPath + '?search=' + sn
    	console.log(url)
	    await fetch(url)
	      .then(r => r.json())
	      .then(data => {
	        console.log(data);
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

	/*onMount(async () => {
		let screenName = getScreenNameValue();
			if ( screenName ) {
				socialusers = await fetchApi();
			}
		}
    );*/
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
      <li><img src="{socialuser.profile.biggeravatar}" alt="user avatar"/></li>
      <li>SocialUser id: {socialuser.id}</li>
      <li><a href="https://twitter.com/intent/user?user_id={socialuser.profile.json.id_str}" target="_blank">🔗 Twitter profile</a></li>
      <li>Twitter user id: {socialuser.user_id}</li>
      <li>Twitter screen name: {socialuser.profile.json.screen_name}</li>
      <li>Twitter name: {socialuser.profile.json.name}</li>
      <li>category<ul>{#each socialuser.category as cat}<li>{cat.label}</li>{/each}</ul></li>
      <li><a href="/admin/moderation/socialuser/{socialuser.id}/change/" target="_blank">🔗 SocialUser admin</a>
      <li>Health Care Provider <HealthCareProvider bind:humanId={socialuser.human[0].id}/></li>
    </ul>
    </div>
    {/each}
  {/if}
  {/key}
	  
<style>
		ul { 
			text-align: left; 
			}
</style>