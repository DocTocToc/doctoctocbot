<script>
  import Discipline from "./Discipline.svelte";
  let disciplines;
  let diplomas = "";
  
      async function fetch_disciplines() {
	    await fetch(`/choice/api/discipline/`)
	      .then(r => r.json())
	      .then(data => {
	        disciplines = data;
	      });
	    console.log({disciplines});
	    return disciplines;
	  };

      async function fetch_diplomas() {
  	    await fetch(`/choice/api/diploma/`)
  	      .then(r => r.json())
  	      .then(data => {
  	        diplomas = data;
  	      });
  	    console.log({diplomas})
  	    return diplomas;
  	  };
</script>

	
    {#await fetch_disciplines() then disciplines}
    {#await fetch_diplomas() then diplomas}
      {#each disciplines as discipline (discipline.id) }	
	
	<!-- Button trigger modal -->
	<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal{discipline.id}">
	  {discipline.label}
	</button>


	<!-- Modal -->
	<div class="modal fade" id="exampleModal{discipline.id}" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
	  <div class="modal-dialog">
	    <div class="modal-content">
	      <div class="modal-header">
	        <h5 class="modal-title" id="exampleModalLabel">{discipline.label}</h5>
	        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
	          <span aria-hidden="true">&times;</span>
	        </button>
	      </div>
	      <div class="modal-body">
	      

	          <Discipline discipline={discipline} diplomas={diplomas} />

	      
	      </div>
	      <div class="modal-footer">
	        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
	      </div>
	    </div>
	  </div>
	</div>
    {/each}
  {/await}
{/await}