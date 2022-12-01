<script>
    import { onMount } from 'svelte';
	export let humanId;
	export let entityId;
	let devUrl = "https://local.doctoctoc.net"
	let apiPath = "/hcp/api/hcp/";
	let domainName = window.location.hostname;
	let hcp;
	let data;
	let apiProtocolDomain = "https://local.doctoctoc.net";
	let queryString;

	onMount(async () => {
		data = await fetchApi();
		console.log(humanId);
	});
	
	function getApiUrl() {
		if (entityId) {
		    queryString = "?entity__id=" + entityId;
		} else {
			queryString = "?human__id=" + humanId;
		}
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
	function getAddUrl() {
		let queryString = entityId ? `?entity=${entityId}` : `?human=${humanId}`;
		return `${getBaseUrl()}/admin/hcp/healthcareprovider/add/${queryString}`
	}
</script>

{#await fetchApi() then data}
<ul>
{#if data.length == 0}
<li>
<a href="{getAddUrl()}" target="_blank">🆕 create HealthCareProvider</a>
</li>
{/if}
{#each data as hcp}
<li>
  <a href="{getBaseUrl()}/admin/hcp/healthcareprovider/{hcp.id}/change/" target="_blank">✏️ edit HealthCareProvider</a>
</li>
  {#each hcp.taxonomy as taxonomy}
    <li>
      {taxonomy.grouping} | {taxonomy.classification} {taxonomy.specialization}
    </li>
  {/each}
{/each}
</ul>
{:catch error}
	<p style="color: red">{error.message}</p>
{/await}
