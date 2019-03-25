$(document).ready(function() {
    $('#option10').focus(function(){
        $('#id_preset_amount').val('10');
    });
    $('#option25').focus(function(){
        $('#id_preset_amount').val('25');
    });
    $('#option50').focus(function(){
        $('#id_preset_amount').val('50');
    });
    $('#option100').focus(function(){
        $('#id_preset_amount').val('100');
    });
    $('#option250').focus(function(){
        $('#id_preset_amount').val('250');
    });
    $('#option500').focus(function(){
        $('#id_preset_amount').val('500');
    });
    $('#option1000').focus(function(){
        $('#id_preset_amount').val('1000');
    });
});

$( "#id_custom_amount" ).focus(function(){
	 $( "#id_preset_amount" ).val('');
	 $('.btn-group').find('label').removeClass('active')
	  .end().find('[type="radio"]').prop('checked', false);
});
    
$( "#amount-radio-group" ).click(function(){
    $( "#id_custom_amount" ).val('');
   });

$(document).ready(function(){
	$( "#option50" ).trigger( "click" );
});