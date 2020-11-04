<script>
import FlatpickrCss from "./FlatpickrCss.svelte";
import Flatpickr from 'svelte-flatpickr';
import French from "flatpickr/dist/l10n/fr.js";
import { _ , getLocaleFromNavigator } from "svelte-i18n";

export let from_datetime_query = "";
export let to_datetime_query = "";

let myElement;

let epoch = "2012-06-06";

let from_datetime = "";
let to_datetime = "";

let now = new Date();

let dates = {
  simple: new Date(),
  range: epoch + " to " + now.toISOString().slice(0,10)
};

function getLocale() {
	// getLocaleFromNavigator returns fr-FR
	// we need to set locale to fr
	var extLocale = getLocaleFromNavigator();
    var shortLocale = extLocale.substring(0, extLocale.indexOf("-"));
    return shortLocale
}

const flatpickrOptionsRange = {
  mode: "range",
  locale: getLocale(),
  element: '#my-picker',
  enableTime: true,
  onChange: (selectedDates, dateStr, instance) => {
	  /*console.log(`Options onChange handler:\n \
	  selectedDates: ${selectedDates} ${typeof(selectedDates[0])} \n \
	  dateStr: ${dateStr} ${typeof(dateStr)}`)*/
      try {
	    if ( selectedDates.length > 1 ) {
    	  from_datetime = selectedDates[0].toISOString();
	      //console.log(`from_datetime: ${from_datetime}`);
	      to_datetime = selectedDates[1].toISOString();
	      //console.log(`to_datetime: ${to_datetime}`);
	    }
      } catch (error) {
	  console.error(error);
	  // expected output: ReferenceError: nonExistentFunction is not defined
	  // Note - error messages will vary depending on browser
	  }
    try {
      if ( from_datetime.length > 0 ) {
        from_datetime_query = `&from_datetime=${from_datetime}`;
      }
      if ( to_datetime.length > 0 ) {
        to_datetime_query = `&to_datetime=${to_datetime}`;
      }
    } catch (error) {
    	console.log(error);
    }
  }
};

function reset() {
	from_datetime = epoch;
	from_datetime_query = `&from_datetime=${epoch}`;
	var now = new Date();
	to_datetime =  now.toISOString().slice(0,10);
	to_datetime_query = `&to_datetime=${to_datetime}`;
}

</script>

<style global>
@import "flatpickr/dist/flatpickr.css";
@import "flatpickr/dist/themes/light.css";
</style>

<Flatpickr
options={flatpickrOptionsRange}
element="#my-picker"
class="form-control datepicker bg-white"
defaultDate={dates.range}
placeholder={dates.range}
>

<div class="flatpickr" id="my-picker">
<input type="text" placeholder="{$_("flatpickr.select", { default: "Select dates.." })}" data-input>

<button type="button" class="btn btn-primary input-button" data-clear on:click={reset}>
{$_("flatpickr.button_clear", { default: "Clear" })}
</button>
</div>

</Flatpickr>
