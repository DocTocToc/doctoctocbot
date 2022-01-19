<script>
    import { sTypeJsn, sDiplomaJsn, diplomaIsDirty } from './stores.js';
    import { sSchool, sSchoolLabel, sSchoolSlug } from './stores.js';
    import Type from "./Type.svelte";
    import Disciplines from "./Disciplines.svelte";
    import CreateRoom from "./CreateRoom.svelte";
    import ParticipantRoom from "./ParticipantRoom.svelte";
    import { roomIsDirty } from './stores.js';

    export function set_sSchool(newValue) {
        $sSchool = newValue;
      }
    export function get_sSchool() {
        return $sSchool;
      }
    export function set_sSchoolLabel(newValue) {
        $sSchoolLabel = newValue;
      }
    export function get_sSchoolLabel() {
        return $sSchoolLabel;
      }
    export function set_sSchoolSlug(newValue) {
        $sSchoolSlug = newValue;
      }
    export function get_sSchoolSlug() {
        return $sSchoolSlug;
      }
</script>

<main>
    {#key $roomIsDirty}
      <ParticipantRoom />
    {/key}
    
    <CreateRoom />

	<form>
	  <div class="form-group row">
	    <label class="col-sm-2 col-form-label">Statut</label>
	    <div class="col-sm-10"><Type /></div>
      </div>
      <div class="form-group row">
        <div class="col-sm-2 col-form-label">
          DES
        </div>
        <div class="col-sm-10">
        {#key $diplomaIsDirty}
          <Disciplines />
        {/key}
        </div>
	  </div>
	<form>
</main>

<style>
</style>