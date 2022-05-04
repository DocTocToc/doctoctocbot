import { readable } from "svelte/store";
const uri = '/community/api/v1/community/language/';

type CommunityLanguage = {
    id: number;
    name: string;
    language: string;
}
const initialData: CommunityLanguage = {id: 0, name: '', language: ''};
export const communityLanguage = readable(initialData, (set) => {
	async () => {
		const response = await fetch(uri);
		const result = await response.json();
		set(result);
	}
});