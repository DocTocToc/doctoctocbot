<style>
    .onoffswitch {
        position: relative; width: 90px;
        -webkit-user-select:none; -moz-user-select:none; -ms-user-select: none;
    }
    .publicprivateswitch {
        position: relative; width: 100px;
        -webkit-user-select:none; -moz-user-select:none; -ms-user-select: none;
    }
    .onoffswitch-checkbox {
        display: none;
    }
    .onoffswitch-label {
        display: block; overflow: hidden; cursor: pointer;
        border: 2px solid #999999; border-radius: 20px;
    }
    .onoffswitch-inner {
        display: block; width: 200%; margin-left: -100%;
        transition: margin 0.3s ease-in 0s;
    }
    .onoffswitch-inner:before, .onoffswitch-inner:after {
        display: block; float: left; width: 50%; height: 30px; padding: 0; line-height: 30px;
        font-size: 14px; color: white; font-family: Trebuchet, Arial, sans-serif; font-weight: bold;
        box-sizing: border-box;
    }
    .onoffswitch-inner:before {
        content: "ON";
        padding-left: 10px;
        background-color: #34A7C1; color: #FFFFFF;
    }
    .publicprivateswitch-inner:before {
        content: "PUBLIC";
        padding-left: 10px;
        background-color: #34A7C1; color: #FFFFFF;
    }
    .onoffswitch-inner:after {
        content: "OFF";
        padding-right: 10px;
        background-color: #EEEEEE; color: #999999;
        text-align: right;
    }
    .publicprivateswitch-inner:after {
        content: "PRIVATE";
        padding-right: 10px;
        background-color: #EEEEEE; color: #999999;
        text-align: right;
    }
    .onoffswitch-switch {
        display: block; width: 18px; margin: 6px;
        background: #FFFFFF;
        position: absolute; top: 0; bottom: 0;
        right: 56px;
        border: 2px solid #999999; border-radius: 20px;
        transition: all 0.3s ease-in 0s; 
    }
    .publicprivateswitch-switch {
        display: block; width: 18px; margin: 6px;
        background: #FFFFFF;
        position: absolute; top: 0; bottom: 0;
        right: 66px;
        border: 2px solid #999999; border-radius: 20px;
        transition: all 0.3s ease-in 0s; 
    }
    .onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-inner {
        margin-left: 0;
    }
    .onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-switch {
        right: 0px; 
    }
</style>
<script>
    import Cookies from 'js-cookie';
    var csrftoken = Cookies.get('csrftoken');
    console.log(`csrttoken:${csrftoken}`)
    export let option = {option};
    let headers = new Headers();
    headers.append('Accept', 'application/json')
    headers.append('Content-Type', 'application/json')
    const config = {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
                body: JSON.stringify({'option': option})
            }
    let promise = getOptin();
    async function getOptin() {
       const config = {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
                body: JSON.stringify({'option': option})
        }
        const res = await fetch(`http://development.doctoctoc.net/optin/api/get/`, config);
        const res_jsn = await res.json();
        if (res.ok) {
            return res_jsn;
        } else {
            throw new Error(text);
        }
    }
    
    async function toggleOptin() {
        const config = {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${csrftoken}`,
                },
                body: JSON.stringify({'option': option})
        }
        const res = await fetch(`http://development.doctoctoc.net/optin/api/update/`, config);
        const res_jsn = await res.json();
        if (res.ok) {
            return res_jsn;
        } else {
            throw new Error(text);
        }
    }
</script>

{#await promise}
      <p>Data loading...</p>
{:then res_jsn}
   <div class="card" style="width: 18rem;">
     <div class="card-body">
       <h5 class="card-title">{res_jsn["label"]}</h5>
       <p class="card-text">{res_jsn["description"]}</p>
         <div class="onoffswitch">
           <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="{option}-switch" checked={res_jsn["authorize"]} on:change={toggleOptin}>
           <label class="onoffswitch-label" for="{option}-switch">
           <span class="onoffswitch-inner"></span>
           <span class="onoffswitch-switch"></span>
           </label>
         </div>
     </div>
   </div>
{:catch error}
    <p style="color: red">{error.message}</p>
{/await}

