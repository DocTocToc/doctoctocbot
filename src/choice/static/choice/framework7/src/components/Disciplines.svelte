<script>
  import { onMount } from "svelte";
  import Discipline from "./Discipline.svelte";
  
  import {
	    List,
	    ListItem
	  } from 'framework7-svelte';
  // define the data holding variable
  let disciplines;
  let diplomas;
  
      async function fetch_disciplines() {
	    await fetch(`https://local.doctoctoc.net/choice/api/discipline/`)
	      .then(r => r.json())
	      .then(data => {
	        disciplines = data;
	      });
	    return disciplines;
	  }

      async function fetch_diplomas() {
  	    await fetch(`https://local.doctoctoc.net/choice/api/diploma/`)
  	      .then(r => r.json())
  	      .then(data => {
  	        diplomas = data;
  	      });
  	    return diplomas;
  	  }

</script>


<List>
  <ListItem title="Diploma" smartSelect smartSelectParams={{openIn: 'popup', searchbar: true, searchbarPlaceholder: 'Search diploma'}}>
    <select name="diploma">
      {#await fetch_disciplines() then disciplines}
        {#await fetch_diplomas() then diplomas}
          {#each disciplines as discipline }
            <Discipline discipline={discipline} diplomas={diplomas} />
          {/each}
        {/await}
      {/await}
    </select>
  </ListItem>
</List>