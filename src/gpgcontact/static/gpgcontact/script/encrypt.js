openpgp = typeof window !== 'undefined' && window.openpgp ? window.openpgp : require('openpgp.js');

async function encryptFunction(str) {
    const options = {
        message: openpgp.message.fromText(str),
        publicKeys: (await openpgp.key.readArmored(pubkey_encrypt)).keys,
    };
    cipher =  await openpgp.encrypt(options);
    ciphertext = cipher.data;
    console.log("ciphertext:");
    console.log(ciphertext);
    $('#id_message').val(ciphertext);
    $('#id_message').change();
    return ciphertext;
}

async function signFunction(str) {
	var signed, signed_text, privateKeys;
	var privKeyObj = (await openpgp.key.readArmored(privkey_sign_4096)).keys;
	const options = {
		message: openpgp.cleartext.fromText(str),
		privateKeys: privKeyObj,
	};
    signed = await openpgp.sign(options);
    console.log("freshly signed:\n" + signed.data)
 	// signed_text = signed.signature;
    return signed.data;

}

var encryptSign = async function(str) {
    const encrypted = await encryptFunction(str);
    console.log("encrypted:\n" + encrypted)
    const signed = await signFunction(encrypted);
    console.log("signed:\n"+ signed);
    $('#id_ciphertext').val(signed);
    $('#form').submit();
}

function validateEmail($email) {
	 var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,8})?$/;
	 if (!emailReg.test($email)) {
	 return false;
	 } else {
	 return true;
	 }
}

$(function() {
	$('#content').on( 'change keyup keydown paste cut', 'textarea', function (){
		var parentElement = document.getElementById("id_message");
		fontSizePx = parseFloat(getComputedStyle(parentElement).fontSize);
		pixel = fontSizePx * 2;
	    $(this).height(0).height(this.scrollHeight + pixel);
	}).find( 'textarea' ).change();
	
    $('#send').on("click", function(e) {
    	var clearText = "Name: " + $('#id_name').val() + "\n" +
     	                "Email: " + $('#id_email').val() + "\n" +
    	                "Message: " + $('#id_message').val();
    	console.log(clearText)
		encryptSign(clearText)
	});
});