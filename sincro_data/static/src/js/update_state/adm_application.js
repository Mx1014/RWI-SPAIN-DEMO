odoo.define('sincro.data.adm.admission', require => {

    require('web.core');

    function fixedError() {
        var element = this;

    }

    $(document).ready(() => {
//        toggleParentListInTextinput();
        $('.fix_btn').on('click', fixedError);
    });

});