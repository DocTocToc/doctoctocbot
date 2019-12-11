<script>
    import { dictionary, locale, locales } from 'svelte-i18n';
    import { _ } from 'svelte-i18n';
    import Cookies from 'js-cookie';

    function createInvoice(event) {
    	console.log("hello");
        console.log(event.target.value);
        return;
    }

    function local_date(date) {
        var d = new Date(date);
        var l_d = d.toLocaleDateString();
        return l_d;
    }

    dictionary.set({
        en: {
            table: {
                date: 'Date',
                purchase: 'Purchase',
                amount: 'Amount',
                invoice: 'Invoice',
            },
        },
        fr: {
            table: {
                date: 'Date',
                purchase: 'Achat',
                amount: 'Montant',
                invoice: 'Facture',
            },
        },
    });
    locale.set('fr');
    
    var csrftoken = Cookies.get('csrftoken');
    console.log(`csrttoken:${csrftoken}`)
    //export let option = {option};
    let headers = new Headers();
    headers.append('Accept', 'application/json')
    headers.append('Content-Type', 'application/json')
    const config = {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
            }
    let promise = getTransaction();
    async function getTransaction() {
       const config = {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
        }
        const res = await fetch(`http://127.0.0.1/financement/api/projectinvestment/`, config);
        const res_jsn = await res.json();
        if (res.ok) {
            console.log(`res_jsn:${res_jsn[0]["project"]}`);
            return res_jsn;
        } else {
            throw new Error(text);
        }
    }
/*    
    async function toggleOptin() {
        const config = {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
        }
        const res = await fetch(`http://127.0.0.1/optin/api/update/`, config);
        const res_jsn = await res.json();
        if (res.ok) {
            return res_jsn;
        } else {
            throw new Error(text);
        }
    }
*/
</script>

<select bind:value={$locale}>
{#each $locales as locale}
  <option value={locale}>{locale}</option>
{/each}
</select>

<table class="table">
<thead>
  <tr>
    <th scope="col">#</th>
    <th scope="col">{$_('table.date')}</th>
    <th scope="col">{$_('table.purchase')}</th>
    <th scope="col">{$_('table.amount')}</th>
    <th scope="col">{$_('table.invoice')}</th>
  </tr>
</thead>
<tbody>

{#await promise}
<tr>
<th scope="row">1</th>
<td>Data loading...</td>
<td>Data loading...</td>
<td>Data loading...</td>
</tr>
{:then res_jsn}
{#each res_jsn as purchase, i}
  <tr>
    <th scope="row">{i + 1} pk:{purchase["pk"]}</th>
    <td>{local_date(purchase["datetime"])}</td>
    <td>{purchase["project"]}</td>
    <td>{purchase["pledged"]}</td>
    <td><button class="btn btn-primary" value="{purchase['pk']}" on:click={createInvoice}>Create</button></td>
  </tr>
  {/each}
{:catch error}
<p style="color: red">{error.message}</p>

{/await}

</tbody>
</table>