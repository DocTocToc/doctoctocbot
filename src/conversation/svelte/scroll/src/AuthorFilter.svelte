<script>
  import { addMessages, init, _, getLocaleFromNavigator } from "svelte-i18n";
  import en from "../public/lang/en.json";
  import fr from "../public/lang/fr.json";
  addMessages("en", en);
  addMessages("fr", fr);
  import Chip, { Set, Text } from '@smui/chips';
  export let authorQuery = '';

  let choices = [
	    { k: 'all', v: $_("status_author_all") },
	    { k: 'self', v: $_("status_author_self") }
	  ];
  
  //let selected = { k: 'all', v: $_("status_author_all") };
  let selected = choices[0];


  $: if ( selected && 'all' == selected.k ) {
	  authorQuery = '';
	}
  $: if ( selected && 'self' == selected.k ) {
	  authorQuery = '&author=self';
	}
</script>

<h4>{$_("status_author")}</h4>
<Set chips={choices} let:chip key={(chip) => chip.k} choice bind:selected>
  <Chip {chip}>
    <Text>{chip.v}</Text>
  </Chip>
</Set>