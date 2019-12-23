<script>
    import { dictionary, locale, locales } from 'svelte-i18n';
    import { _ } from 'svelte-i18n';
    import Cookies from 'js-cookie';
	import { onMount } from 'svelte';

    let myButton;
    onMount(() => {
    	getCustomer().then(customer_jsn => {
    		console.log(customer_jsn);
        	console.log(customer_jsn[0]);
        	console.log(customer_jsn[0]["empty_fields"]);
        	if (!(customer_jsn[0]["empty_fields"]==="")) {
        	    myButton.disabled=true;
        	    myButton.classList.toggle("btn-warning");
        	    myButton.classList.toggle("btn-primary");
        	    myButton.innerHTML = "Complétez le formulaire.";
        	}
        });
    });


    async function postInvoice(event) {
        console.log(event.target.value);
        const config = {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
                body: JSON.stringify({'uuid': event.target.value})
        }
        const res = await fetch(`/customer/api/invoice/`, config);
        const res_jsn = await res.json();
        if (res.ok) {
            console.log(JSON.stringify(res_jsn));
            return res_jsn;
        } else {
            throw new Error(text);
        }
    }
    
    function local_date(date) {
        var d = new Date(date);
        var l_d = d.toLocaleDateString();
        return l_d;
    }

    function disable_button() {
        document.getElementsByClassName("btn-primary").disabled = true;
    }
    function enable_button() {
        document.getElementsByClassName("btn-primary").disabled = false;
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
    $: promise_transaction = getTransaction();
    async function getTransaction() {
       const config = {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
        }
        const res = await fetch(`/financement/api/projectinvestment/`, config);
        var res_jsn = await res.json();
        if (res.ok) {
        	var str = JSON.stringify(res_jsn, null, 2);
            console.log(`res_jsn:${str}`);
            return res_jsn;
        } else {
            throw new Error(text);
        }
    }

    function createInvoice(event) {
    	if (confirm("Avez-vous vérifié l'exactitude de vos informations de facturation?")) {
        	console.log("confirmed");
            console.log(event.target.value);
            postInvoice(event);
            var delayInMilliseconds = 3000; //1 second
            setTimeout(function() {
            	promise_transaction = getTransaction();
            }, delayInMilliseconds);
            return;
    	}
    }

    let promise_customer = getCustomer();
    async function getCustomer() {
       const config = {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
        }
        const res = await fetch(`/customer/api/customer/`, config);
        const customer_jsn = await res.json();
        if (res.ok) {
        	var str = JSON.stringify(customer_jsn, null, 2);
        	var k;
            console.log(`customer_jsn:${str}`);
            var empty_fields = [];
            var dct = customer_jsn[0];
            for (k in dct) {
            	console.log(`k:${k}`);
            	console.log(`dct[k]:${dct[k]}`);
                if (dct[k] === "" || dct[k]==null) {
            	    empty_fields.push(k);
            	}
            }
            console.log(`empty_fields:${empty_fields}`);
            var empty_fields_list = "";
            if (empty_fields.length) {
                empty_fields_list = empty_fields.join(", ");
                disable_button();
            } else {
            	enable_button();
            }
            customer_jsn[0]["empty_fields"] = empty_fields_list;
            return customer_jsn;
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

{#await promise_transaction}
<tr>
<th scope="row">1</th>
<td>Data loading...</td>
<td>Data loading...</td>
<td>Data loading...</td>
</tr>
{:then res_jsn}
{#each res_jsn as purchase, i}
  <tr>
    <th scope="row">{i + 1}</th>
    <td>{local_date(purchase["datetime"])}</td>
    <td>{purchase["project"]}</td>
    <td>{purchase["pledged"]}</td>
    <td>
    {#if (purchase["invoice_pdf"])}
    <a href='/silver/invoices/{purchase["invoice"]}.pdf'>Pdf</a>
    {:else}
    <button class="btn btn-primary" bind:this={myButton} value="{purchase['pk']}" on:click={createInvoice}>Create</button>
    {/if}
    </td>
  </tr>
  {/each}
{:catch error}
<p style="color: red">{error.message}</p>

{/await}

</tbody>
</table>

{#await promise_customer}
<p>...</p>
{:then customer_jsn}
{#each customer_jsn as customer}
{#if (customer["empty_fields"])}
<p>Pour nous permettre d'éditer votre facture, merci de compléter: {customer["empty_fields"]}.</p>
{/if}
{/each}
{:catch error}
<p style="color: red">{error.message}</p>
{/await}