<script>
  // create a prop
  export let discipline;
  export let diplomas;
</script>

<optgroup label={discipline.label}>
    {#each diplomas as diploma }
      {#if diploma.discipline == discipline.id}
        <option value={diploma.id}>{diploma.label}</option>
      {/if}
    {/each}
</optgroup>