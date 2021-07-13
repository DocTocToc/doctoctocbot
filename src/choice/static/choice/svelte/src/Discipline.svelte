<script>
  import { sDiplomaJsn } from './stores.js';

  export let discipline;
  export let diplomas;
  //export let selectedDiploma = "";
  //$: console.log(selectedDiploma);
</script>

{#each diplomas as diploma }
  {#if diploma.discipline == discipline.id}
  	  <div class="form-check">
      <label class="form-check-label">
	    <input bind:group={$sDiplomaJsn} type="radio" class="form-check-input" name="exampleRadios" value={diploma} />
	        {diploma.label}
	    </label>
	    </div>
  {/if}
{/each}