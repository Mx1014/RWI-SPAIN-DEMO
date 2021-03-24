odoo.define('adm_formio.upload_file', require => {

    require('web.core');

    $(document).ready(() => {

        const $sentFormioEmail = $(document.getElementById('sent_formio_email'));
        $sentFormioEmail.find('button').on('click', event => {
            $('.js_hide_if_sent').hide();
            $('.js_show_if_sent').show();

            const email = $sentFormioEmail.find('input').prop('disabled', true).val();
            const applicationId = $('meta[name="_application_id"]').attr("value");//$('meta[name="_application_id"]').val();

            $.ajax({
                url: '/admission/applications/' + applicationId + '/formio/email',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({'email': email}),
                csrf_token: odoo.csrf_token,
                beforeSend: () => {
                    $(document.getElementById('adm_loader')).show();
                },
                success: () => {location.reload();},
                error: (error) => {
                    $(document.getElementById('adm_loader')).hide();
                    $('.js_hide_if_sent').show();
                    $('.js_show_if_sent').hide();
                    $sentFormioEmail.find('input').prop('disabled', false);

                    const errorResponse = error.responseJSON;

                    $(document.getElementById('errorDialog')).modal('show');
                    $('.js_error_text').text(errorResponse.result);
                },
            })
        });

    });

});