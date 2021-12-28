(function($) {
    $(function() {
        $('textarea.textareacounter').change(function(e) {
            e.preventDefault();
            $(this).siblings('.counter').find('.input-counter').html(
                $(this).val().length
            );
        });
        $('textarea.textareacounter').keyup(function(e) {
            $(this).change();
        })
    })
})(django.jQuery);