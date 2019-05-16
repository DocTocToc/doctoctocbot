<div id="app">
  {{#if (jsn == null)}}
      <p>Data loading...</p>
      {{else}}
  <div>
    <!--p class="invisible">SocialUser: {{jsn.socialuser}} Active: {{jsn.active}}</p-->
    <div class="onoffswitch">
        <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="activeswitch" checked={{jsn.active}} on:change=patch()>
        <label class="onoffswitch-label" for="activeswitch">
            <span class="onoffswitch-inner"></span>
            <span class="onoffswitch-switch"></span>
        </label>
    </div>
    <div class="onoffswitch publicprivateswitch">
        <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="publicprivateswitch" checked={{jsn.public}} on:change=patch()>
        <label class="onoffswitch-label" for="publicprivateswitch">
            <span class="onoffswitch-inner publicprivateswitch-inner"></span>
            <span class="onoffswitch-switch publicprivateswitch-switch"></span>
        </label>
    </div> 
 
  </div>
  {{/if}}
  
</div>

<script type="text/javascript">
  var Cookies = require('js-cookie');
  var csrftoken = Cookies.get('csrftoken');
  console.log(`csrttoken:${csrftoken}`)

  const socialuserid = document.getElementById('socialuserid').innerHTML;
  console.log(`socialuserid:${socialuserid}`)


  
  // async data fetching function
  const fetchModerator = async (data, component) => {
    const response = await fetch(`${window.location.origin}/moderators/${socialuserid}/`);
    const json = await response.json();
    const jsn = json;
    console.log(jsn);
    component.set({ jsn });
  };

  
  const patchModerator = async (data) => {
      console.log(socialuserid);
	  const url = `${window.location.origin}/moderators/${socialuserid}/`;
	  var active = document.getElementById("activeswitch").checked;
	  var _public = document.getElementById("publicprivateswitch").checked;
	  
	  const body = {'active': active, 'public': _public};
	  console.log(body);
	  try {
		    const config = {
		        method: 'PATCH',
		        headers: {
		            'Accept': 'application/json',
		            'Content-Type': 'application/json',
		            'X-CSRFToken': `${csrftoken}`,
		        },
		        body: JSON.stringify(body)
		    }
		    const response = await fetch(url, config)
		    const json = await response.json()
		    if (response.ok) {
		        console.log(json)
		        return response
		    } else {
		        //
		    }
		} catch (error) {
		        //
		}
	};

  // export the default object
  export default {
    oncreate() {
      let data = this.get();
      fetchModerator(data, this);
    },
    methods: {

      patch() {
	    let data = this.get();
        patchModerator(data, this);
      },
    },
    components: {
    }
  };
</script>

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
