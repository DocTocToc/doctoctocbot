<script>
  import { sTypeJsn, defaultJsn } from './stores.js';
  let types;

      async function fetch_types() {
	    await fetch(`/choice/api/participant-type/`)
	      .then(r => r.json())
	      .then(data => {
	        types = data;
	      });
	    console.log({types});
	    return types;
	  };
</script>

{#await fetch_types() then types}
  <select bind:value={$sTypeJsn} class="custom-select" id="selectType">
    <option value={defaultJsn} selected>Statut</option>
    {#each types as type (type.id) }	
      <option value={type}>{type.label}</option>
    {/each}
  </select>
{/await}
