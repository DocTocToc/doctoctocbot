<script>
    import { onMount } from 'svelte';
	export let humanId;
	let devUrl = "https://local.doctoctoc.net"
	let apiPath = "/hcp/api/hcp/";
	let domainName = window.location.hostname;
	let hcp;
	let data;
	let apiProtocolDomain = "https://local.doctoctoc.net";

	onMount(async () => {
		data = await fetchApi();
		console.log(humanId);
	});
	
	function getApiUrl() {
		let queryString = "?human__id=" + humanId;
	    if (window.location.hostname == "localhost") {
	    	return devUrl + apiPath + queryString
	    } else {
	    	return apiPath + queryString
	    }
	}

    async function fetchApi() {
    	let url = getApiUrl();
    	console.log(url);
        let response = await await fetch(url);
        let data = await response.json();
    	console.log(data);
	    return data;
	};
	
	function getBaseUrl() {
	    if (window.location.hostname == "localhost") {
	    	return apiProtocolDomain
	    } else {
	    	return ""
	    }
	}	
</script>

{#await fetchApi() then data}
<ul>
{#if data.length == 0}
<li>
<a href="{getBaseUrl()}/admin/hcp/healthcareprovider/add/?human={humanId}" target="_blank">🔗 HealthCareProvider admin</a>
</li>
{/if}
{#each data as hcp}
<li>
  <a href="{getBaseUrl()}/admin/hcp/healthcareprovider/{hcp.id}/change/" target="_blank">🔗 HealthCareProvider admin</a>
</li>
  {#each hcp.taxonomy as taxonomy}
    <li>
      {taxonomy.grouping} | {taxonomy.classification} {taxonomy.specialization}
    </li>
  {/each}
{/each}
</ul>
{/await}
