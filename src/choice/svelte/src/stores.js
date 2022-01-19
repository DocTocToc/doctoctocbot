import { writable, get } from 'svelte/store';

export const defaultJsn = {id:null, label:"", slug:""};

export const sDiplomaJsn = writable(defaultJsn);
export const sTypeJsn = writable(defaultJsn);
export const sSchool = writable('');
export const sSchoolLabel = writable('');
export const sSchoolSlug = writable('');
export const roomIsDirty = writable(0);
export const diplomaIsDirty = writable(0);