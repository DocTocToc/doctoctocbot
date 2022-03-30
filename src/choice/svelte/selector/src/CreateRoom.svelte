<script>
import { sTypeJsn, sDiplomaJsn, sSchool, sSchoolLabel, sSchoolSlug, roomIsDirty, diplomaIsDirty } from './stores.js';

let resCreateRoom = null;
let url;
let buttonRefresh = false;

$: buttonRefresh = $sTypeJsn.label + $sDiplomaJsn.label + $sSchoolLabel

function clearSelect() {
	$sDiplomaJsn.label = "";
	$sSchoolLabel = "";
	$diplomaIsDirty++;
}

async function fetchCreateRoom() {
	url = '/choice/api/create-room/' + $sTypeJsn.slug + '/' + $sSchoolSlug + '/' + $sDiplomaJsn.slug + '/';
	console.log(url)
    await fetch(url)
      .then(r => r.json())
      .then(data => {
        resCreateRoom = data;
      });
    console.log(resCreateRoom);
    $roomIsDirty++;
    clearSelect();
    return resCreateRoom;
  };
</script>

<div class="card">
  <div class="card-body">
    <ul class="list-group list-group-flush">
      <li class="list-group-item">
        {#if $sTypeJsn.label != ""}
        <span class="badge badge-info">{$sTypeJsn.label}</span>
        {:else}
        <p class="text-muted">Statut</p>
        {/if}
      </li>
      <li class="list-group-item">
        {#if $sDiplomaJsn.label != ""}
        <span class="badge badge-info">{$sDiplomaJsn.label}</span>
        {:else}
        <p class="text-muted">DES</p>
        {/if}
      <li class="list-group-item">
        {#if $sSchoolLabel != ""}
        <span class="badge badge-info">{$sSchoolLabel}</span>
        {:else}
        <p class="text-muted">Ville</p>
        {/if}
      </ul>
      {#key buttonRefresh}
      {#if $sTypeJsn.label && $sDiplomaJsn.label && $sSchoolLabel}
        <button on:click={fetchCreateRoom} class="btn btn-outline-primary btn-lg">Ajouter le salon</button>
      {:else}
        <button class="btn btn-outline-muted disabled btn-lg" disabled>Ajouter le salon</button>
      {/if}
      {/key}
      <p class="card-text">Pour rejoindre le salon de discussion et poser des questions ou apporter des réponses, veuillez sélectionner votre statut, un DES et une ville sur la carte.</p>
    </div>
</div>

