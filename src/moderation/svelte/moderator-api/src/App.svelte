<script>
	import { addMessages, init, _, getLocaleFromNavigator } from "svelte-i18n";
    import Toggle from "svelte-toggle";
    let toggledOnOff;
    let toggledPublicPrivate;
    let jsn;
    import Cookies from "../node_modules/js-cookie/dist/js.cookie.mjs";
    const csrftoken = Cookies.get("csrftoken");
    import en from "../public/lang/en.json";
    import fr from "../public/lang/fr.json";

    addMessages("en", en);
    addMessages("fr", fr);

    init({
      initialLocale: "fr",
      initialLocale: getLocaleFromNavigator(),
    });

    async function getModeratorId() {
        let response = await fetch(`/moderation/api/moderator-id/`);
        let data = await response.json();
        let id = data.id;
        return id;
    };

$: onChange(toggledOnOff, toggledPublicPrivate)

    function onChange(...args) {
        patchModerator();
    }

    getModeratorId().then((id) => console.log(`moderator id: ${id}`));

    // async data fetching function
    const fetchModerator = async (data, component) => {
        const id = await getModeratorId();
        const response = await fetch(`/moderation/api/moderators/${id}/`);
        const jsn = await response.json();
        console.log(jsn);
        toggledOnOff=jsn.active;
        toggledPublicPrivate=jsn.public;
        return jsn
    };

    const patchModerator = async (data) => {
        console.log("inside patchModerator()");
        const id = await getModeratorId();
        const url = `/moderation/api/moderators/${id}/`;
        const body = {
            active: toggledOnOff,
            public: toggledPublicPrivate,
        };
        console.log(`id: ${id}, url: ${url}, body: ${body}`);
        try {
            const config = {
                method: "PATCH",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                    "X-CSRFToken": `${csrftoken}`,
                },
                body: JSON.stringify(body),
            };
            const response = await fetch(url, config);
            const json = await response.json();
            if (response.ok) {
                console.log(json);
                return response;
            } else {
                //
            }
        } catch (error) {
            //
        }
    };
	let promise = fetchModerator();
</script>
{#await promise}
... Loading
{:then} 
<Toggle
    label={$_("public_private_label")}
    switchColor="#eee"
    toggledColor="#24a148"
    untoggledColor="#fa4d56"
    on={$_("public")}
    off={$_("private")}
    bind:toggled={toggledPublicPrivate}
/>
<Toggle
    label={$_("on_off_label")}
    switchColor="#eee"
    toggledColor="#24a148"
    untoggledColor="#fa4d56"
    on="On"
    off="Off"
    bind:toggled={toggledOnOff}
/>
{/await}