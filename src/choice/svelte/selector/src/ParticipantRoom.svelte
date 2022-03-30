<script>
  import { sSchoolSlug, sDiplomaJsn, roomIsDirty } from './stores.js';
  import { onMount } from 'svelte';
  let rooms;
  let hasActiveRoom = true;
  
      async function fetchRooms() {
	    await fetch(`/choice/api/participant-room/`)
	      .then(r => r.json())
	      .then(data => {
	        rooms = data[0].room;
	      })
	      .then(rooms => {if (rooms) hasActiveRoom = activeRoom(rooms);
	      })
	    console.log({rooms});
	    return rooms;
	  };
	  
      async function fetchInactivateRooms(diplomaSlug, schoolSlug) {
   		  let url = '/choice/api/inactivate-room/' + schoolSlug + '/' + diplomaSlug  + '/';
          console.log(url)
  	      await fetch(url).then(response => {
  	          if (response.ok) {
  	  	          hasActiveRoom = activeRoom(rooms);
  	  	          $roomIsDirty++;
  	  	          console.log(response);
  	          }
  	      })
      };
  	  
  	 function activeRoom(rooms) {
  		 let active = false;
  		 for (let room of rooms) {
  			 if (room.active) active=true;
  		 }
  		 return active
  	 }
  	 
  	onMount(async () => {
		 rooms = await fetchRooms();
		 hasActiveRoom = activeRoom(rooms)
	});
</script>

{#key roomIsDirty}
{#await fetchRooms() then rooms}
{#if hasActiveRoom}
  <div class="card">
    <div class="card-header">
      Mes salons
    </div>
    <ul class="list-group">
      {#each rooms as room (room.id) }
        {#if room.active}
          <li
            class="list-group-item">
            <a href="{ room.room_link }" target="_blank" class="my-1 btn btn-outline-primary" role="button" aria-pressed="true">
            { room.diploma.label } | { room.school.tag }
            </a>
            <button class="btn btn-light btn-sm" on:click|once={async () => {await fetchInactivateRooms(room.diploma.slug, room.school.slug)}}>❌</button>
          </li>
        {/if}
      {/each}
    </ul>
  </div>
{/if}
{/await}
{/key}
