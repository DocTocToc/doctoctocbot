<script lang="ts">
  import { onMount } from "svelte";
  import { Input } from "@smui/textfield";
  import Paper from "@smui/paper";
  import Fab from "@smui/fab";
  import { Icon } from "@smui/common";
  import FormField from "@smui/form-field";
  import Radio from "@smui/radio";
  import { addMessages, init, _, getLocaleFromNavigator } from "svelte-i18n";
  import en from "../public/lang/en.json";
  import fr from "../public/lang/fr.json";
  addMessages("en", en);
  addMessages("fr", fr);
  export let searchQuery = "";
  let searchValue = "";
  let inputValue = "";
  let disabled = true;
  let color = "secondary";
  let selected;
  let options = [];
  const uri = "/community/api/v1/community/language/";

  Object.defineProperty(String.prototype, "capitalize", {
    value: function () {
      return this.charAt(0).toUpperCase() + this.slice(1);
    },
    enumerable: false,
  });

  onMount(async () => {
    let defaultLanguage = {
      name: $_("english"),
      code: "en",
    };
    let data = await fetch(uri).then((x) => x.json());
    let lang = data[0];
    console.log(lang);
    let communityLanguage = {
      name: lang.language_name.capitalize(),
      code: lang.language,
    };
    console.log(communityLanguage);
    selected = communityLanguage.code;
    let or = {
      name:
        communityLanguage.name.capitalize() +
        " " +
        $_("or") +
        " " +
        $_("english"),
      code: "null",
    };
    console.log(or);
    options = [communityLanguage, defaultLanguage, or];
    console.log(options);
  });

  $: disabled = !Boolean(inputValue);

  $: color = disabled ? "primary" : "secondary";

  $: searchQuery = searchValue ? ("&search=" + searchValue + "&lang=" + selected) : "";

  function doSearch() {
    searchValue = inputValue;
  }

  function handleKeyDown(event: CustomEvent | KeyboardEvent) {
    event = event as KeyboardEvent;
    if (event.key === "Enter") {
      doSearch();
    }
  }
</script>

<div class="solo-container search-container">
  <Paper class="solo-paper" elevation={6}>
    <Icon class="material-icons">search</Icon>
    <Input
      bind:value={inputValue}
      on:keydown={handleKeyDown}
      placeholder={$_("search")}
      class="solo-input"
    />
  </Paper>
  <Fab on:click={doSearch} {disabled} {color} mini class="solo-fab">
    <Icon class="material-icons">arrow_forward</Icon>
  </Fab>
  </div>
  <div class="solo-container language-container">
  {#each options as option}
    <FormField>
      <Radio bind:group={selected} value={option.code} class="solod-radio" />
      <span slot="label">{option.name}</span>
    </FormField>
  {:else}
    <p>{$_("loading")}</p>
  {/each}
</div>

<style>
  .search-container {
    padding: 36px 18px;
    background-color: var(--mdc-theme-background, #f8f8f8);
    border: 1px solid
      var(--mdc-theme-text-hint-on-background, rgba(0, 0, 0, 0.1));
  }
  .language-container {
    padding: 18px 18px;
    background-color: var(--mdc-theme-background, #f8f8f8);
    border: 1px solid
      var(--mdc-theme-text-hint-on-background, rgba(0, 0, 0, 0.1));
  }

  .solo-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  * :global(.solo-paper) {
    display: flex;
    align-items: center;
    flex-grow: 1;
    max-width: 600px;
    margin: 0 12px;
    padding: 0 12px;
    height: 48px;
  }
  * :global(.solo-paper > *) {
    display: inline-block;
    margin: 0 12px;
  }
  * :global(.solo-input) {
    flex-grow: 1;
    color: var(--mdc-theme-on-surface, #000);
  }
  * :global(.solo-input::placeholder) {
    color: var(--mdc-theme-on-surface, #000);
    opacity: 0.6;
  }
  * :global(.solo-fab) {
    flex-shrink: 0;
  }
  * :global(.solo-radio) {
    flex-grow: 1;
    color: var(--mdc-theme-on-surface, #000);
  }
</style>
