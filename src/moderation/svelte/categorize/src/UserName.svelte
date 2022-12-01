<script>
	import { onMount } from "svelte";
	import CreateSocialUser from "./CreateSocialUser.svelte";
	import HealthCareProvider from "./HealthCareProvider.svelte";
	import dayjs from 'dayjs';
	import customParseFormat from 'dayjs/plugin/customParseFormat';
	import relativeTime from 'dayjs/plugin/relativeTime';
	import 'dayjs/locale/fr'
	dayjs.extend(customParseFormat)
	dayjs.extend(relativeTime)
	let input = "";
	let screenName = "";
	let apiPath = "/moderation/api/socialuser/";
	let screenNameValue = "";
	let socialusers = null;
	let humanId = 0;

	$: {
		let param = new URL(document.location).searchParams.get("screen_name");
		if (param) {
			socialusers = fetchApi(param);
			screenName = param;
			input = param;
		}
	}

	function getScreenNameValue() {
		return new URL(document.location).searchParams.get("screen_name");
	}

	function toHRDate(isoDateTimeString) {
		const date = new Date(isoDateTimeString);
		return date.toDateString();
	}

	function durationFromNow(twitterDateTimeString) {

		//Twitter date time format: "Thu Jun 05 19:56:42 +0000 2014"
		let dateTime = dayjs(twitterDateTimeString, "[ddd] MMM DD HH:mm:ss [zz] YYYY");
		return dateTime.fromNow()
	}

	async function fetchApi(sn) {
		let url = apiPath + "?search=" + sn;
		await fetch(url)
			.then((r) => r.json())
			.then((data) => {
				socialusers = data;
			});
		return socialusers;
	}

	async function onClickFetchApi(input) {
		if (input.startsWith("@")) {
			screenName = input.slice(1);
		} else {
			screenName = input;
		}
		socialusers = await fetchApi(screenName);
	}

	/*onMount(async () => {
		let screenName = getScreenNameValue();
			if ( screenName ) {
				socialusers = await fetchApi();
			}
		}
    );*/
	function getHumanId(socialuser) {
		try {
		    return socialuser.human[0].id
		} catch(err) {
            return null
		}

	}
	function getEntityId(socialuser) {
		try {
		    return socialuser.entity.id
		} catch(err) {
            return null
		}

	}
</script>

<form action="" method="get" on:submit|preventDefault={onClickFetchApi(input)}>
	<label for="screen_name">Enter Twitter screen_name</label>
	<input type="text" name="screen_name" id="screen_name" bind:value={input} />
	<button type="submit" disabled={!input} on:click={onClickFetchApi(input)}
		>Fetch!</button
	>
</form>

{#key socialusers}
	{#if socialusers && socialusers.length == 0 && screenName}
		<p>Utilisateur inconnu dans notre base de données.</p>
		<CreateSocialUser bind:screenName />
	{:else if socialusers}
		{#each socialusers as socialuser (socialuser.id)}
			<div class="parent">
				<ul>
					<li>
						<img
							src={socialuser.profile.biggeravatar}
							alt="user avatar"
						/>
					</li>
					<li>SocialUser id: {socialuser.id}</li>
					<li>
						<a
							href="https://twitter.com/intent/user?user_id={socialuser
								.profile.json.id_str}"
							target="_blank">🔗 Twitter profile</a
						>
					</li>
					<li>Twitter user id: {socialuser.user_id}</li>
					<li>
						Twitter screen name: {socialuser.profile.json
							.screen_name}
					</li>
					<li>Twitter name: {socialuser.profile.json.name}</li>
					<li>Account created {durationFromNow(socialuser.profile.json.created_at)}</li>
					<li>{socialuser.profile.json.description}</li>
					<li>location: {socialuser.profile.json.location}</li>
					<li>statuses count: {socialuser.profile.json.statuses_count}</li>
					<li>favourites count: {socialuser.profile.json.favourites_count}</li>					
					<li>
						category
						<ul>
							{#each socialuser.categoryrelationships as catRel}<li
								>
									<div style="white-space: nowrap">
										{catRel.category.label}
										{#if catRel.moderator}
											{#if catRel.moderator.id == socialuser.id}<mark
													>*</mark
												>{/if} | {catRel.moderator
												.profile.json.screen_name}
										{/if}
										| Created {toHRDate(catRel.created)} | Updated
										{toHRDate(catRel.updated)}
									</div>
								</li>{/each}
						</ul>
					</li>
					<li>
						<a
							href="/admin/moderation/socialuser/{socialuser.id}/change/"
							target="_blank">🔗 SocialUser admin</a
						>
					</li>
					<li>
						Health Care Provider <HealthCareProvider
							humanId={getHumanId(socialuser)}
							entityId={getEntityId(socialuser)}
						/>
					</li>
				</ul>
			</div>
		{/each}
	{/if}
{/key}

<style>
	ul {
		text-align: left;
	}
</style>
