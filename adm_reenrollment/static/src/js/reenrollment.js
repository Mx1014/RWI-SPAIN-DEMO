odoo.define('adm.reenrollment.form', require => {
    "use strict";

    require('web.core');
    const rpc = require('web.rpc')

    const PARTNER_FIELDS = ['first_name', 'middle_name', 'last_name', 'email', 'id_documentation_file_name'];

    async function changePartner(inputPrefix, $partnerGuardianCard, $partnerGuardianSelect) {
        $(document.getElementById('adm_loader')).show();
            const partner = (await rpc.query({
                model: 'res.partner',
                method: 'read',
                args: [[parseInt(($partnerGuardianSelect.val()))]],
                kwargs: {
                    fields: PARTNER_FIELDS
                }
            }))[0];

            let $idInputEl = $partnerGuardianCard.find('input[name=id]');
            let idInputEl;
            if ($idInputEl.length) {
                idInputEl = $idInputEl[0];
            } else {
                idInputEl = document.createElement('INPUT');
                $partnerGuardianCard.append(idInputEl);
            }

            idInputEl.dataset.admField = 'id';
            idInputEl.dataset.admFieldType = 'INTEGER';
            idInputEl.name = 'id';
            idInputEl.type = 'hidden';
            idInputEl.value = partner.id

            document.getElementById(inputPrefix + '_first_name').value = partner.first_name || '';
            document.getElementById(inputPrefix + '_middle_name').value = partner.middle_name || '';
            document.getElementById(inputPrefix + '_last_name').value = partner.last_name || '';

            document.getElementById(inputPrefix + '_email').value = partner.email || '';
            document.getElementById(inputPrefix + '_phone').value = partner.phone || '';

            document.getElementById(inputPrefix + '_phone').value = partner.phone || '';

            $(document.getElementById('adm_loader')).hide();
    }

    $(document).ready(() => {
        const $partnerGuardian1Card = $(document.getElementById('partner_guardian1_card'));
        const $partnerGuardian1Select = $(document.getElementById('partner_guardian1_select'));
        $partnerGuardian1Select.on('change', () => {changePartner('parent1', $partnerGuardian1Card, $partnerGuardian1Select)});

        const $partnerGuardian2Card = $(document.getElementById('partner_guardian2_card'));
        const $partnerGuardian2Select = $(document.getElementById('partner_guardian2_select'));
        $partnerGuardian2Select.on('change', () => {changePartner('parent2', $partnerGuardian2Card, $partnerGuardian2Select)});
    });

});