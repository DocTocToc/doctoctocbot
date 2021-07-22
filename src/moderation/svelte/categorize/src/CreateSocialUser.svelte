<script>
	export let screenName;
	let devUrl = "https://local.doctoctoc.net"
	let createSocialUserPath = "/moderation/api/create-twitter-socialuser/";
	let data;
	let domainName = window.location.hostname
	
	function getApiUrl() {
	    if (window.location.hostname == "localhost") {
	    	return devUrl + createSocialUserPath + screenName + "/"
	    } else {
	    	return createSocialUserPath + screenName + "/"
	    }
	}

    async function fetchApi() {
    	let url = getApiUrl();
    	//console.log(url);
	    await fetch(url)
	      .then(r => console.log(r));
	};
</script>

<button on:click={fetchApi} disabled={!screenName}>Create @{screenName} SocialUser</button>