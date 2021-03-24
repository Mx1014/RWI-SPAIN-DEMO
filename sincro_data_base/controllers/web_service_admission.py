import json

# from formiodata.components import selectboxesComponent

from odoo import http
import datetime
import logging
import re
from odoo.tools.safe_eval import safe_eval

# Se añaden campos:
# - Siblings
# - Datos de los hermanos
# - Horario de partner
# - Comment en res.parthner

# Updated 2020/12/14
# By Luis
# Just some clean up
_logger = logging.getLogger(__name__)


class WebServiceController(http.Controller):
    """ Controlador encargado de devolver datos de las admisiones,
    para insertarlas en FACTS
    """

    def get_value(self, key, value):
        if isinstance(value, dict) and str(key) in value:
            return self.get_value(key, value[key])
        else:
            return value

    # devuelve formato pretty del JSON
    def json_to_pretty_format(self, val, json_pretty):
        if not isinstance(val, list) and not isinstance(val, dict) and isinstance(val, str):
            return val
        for key, item in val.items():
            json_pretty[key] = {}
            if isinstance(item, dict) and str(key) in item:
                # json_pretty[key] = self.json_to_pretty_format(item[key], json_pretty[key])
                json_pretty[key] = self.get_value(key, item[key])
            elif isinstance(item, list):
                json_pretty[key] = []
                for elem in item:
                    json_pretty[key].append({})
                    json_pretty[key].append(self.json_to_pretty_format(elem, json_pretty[key].pop()))
            else:
                json_pretty[key] = self.json_to_pretty_format(item, json_pretty[key])
        return json_pretty

    def compute_domain(self, domain_str):
        res_list = []
        if not domain_str or domain_str in ('', 'False'):
            return res_list
        raw_data = re.split(r',\s*(?![^()]*\))', domain_str[1:-1])
        for val in raw_data:
            if val == "'&'" or val == "'|'":
                res_list.append(val[1:-1])
            else:
                res_list.append(val[1:-1].replace("'", "").split(","))
        return res_list

    def recur_pretty(self, data, res_json):
        if not isinstance(data, dict):
            return data
        else:
            for key, value in data.items():
                if isinstance(value, dict) and str(key) in value:
                    res_json[key] = self.recur_pretty(value, res_json[key])
                else:
                    res_json[key] = value
                self.recur_pretty(value, res_json[key])

        # devuelve la información en formato json dependiendo de la configuracion del webservice

    def get_json_from_config(self, value, data):
        result = ''
        if not value.fields:
            result += '"%s": "%s",' % (value.alias_field, data)
        else:
            result += '"%s":{' % value.alias_field
            if value.field_id.ttype in ('one2many', 'many2many'):
                result = result[0: -1] + '[{'
            for item_data in data:
                # if len(data) > 1:
                for item in value.fields:
                    aux_domain = self.compute_domain(item.domain)
                    aux_val = item_data[item.field_id.sudo().name]
                    # capamos los ids filtrados anteriormente
                    aux_domain = safe_eval(item.domain or "[]")
                    if len(aux_domain) > 0:
                        aux_domain.append(['id', 'in', aux_val.ids])
                        # aux_domain
                        aux_val = item_data[item.field_id.sudo().name].search(aux_domain)

                    result += self.get_json_from_config(item, aux_val)

                if len(data) > 1:
                    # if value.field_id.ttype in ('one2many', 'many2many'):
                    if result[-1] == ',':
                        result = result[0: -1]
                    result += '},{'
                # if len(data) > 1:
            if str(result[-2]) + str(result[-1]) == ',{':
                result = result[0: -3]
            if result[-1] == ',':
                result = result[0: -1]
            if value.field_id.ttype in ('one2many', 'many2many'):
                result += '}]'
            else:
                result += '}'

            result += ','
        return result

    def cleaned_json(self, value, appl):
        raw_res = self.get_json_from_config(value.panel_configuration, appl)
        if raw_res[-1] == ',':
            raw_res = raw_res[0: -1]
        if raw_res[-2::] == '}]':
            raw_res += '}'
        json_res = '{' + raw_res + '}';
        return json_res

    # menos para GET.
    @http.route("/sincro_data/getJSON", auth="public", methods=["GET"], cors='*')
    def get_json(self, **params):

        """ Definiendo la url desde donde va ser posible acceder, tipo de
        metodo,
        cors para habiltiar accesos a ip externas.
        """

        allowed_urls = (http.request.env['ir.config_parameter'].sudo()
                        .get_param('allow_urls', ''))

        origin_url = '-1'
        _logger.info("entro")
        # Array con los campos del alumno y de las familias y los partners
        partner_fields = ["first_name", "middle_name", "last_name"]

        # tomamos los campos seleccionados en la opcion
        config_parameter = http.request.env['ir.config_parameter'].sudo()
        field_ids = config_parameter.get_param('adm_application_json_field_ids', False)

        search_domain = []
        required_status_ids = []
        required_status_str = config_parameter.get_param('required_status_ids', False)
        if required_status_str:
            required_status_ids = [
                int(e) for e in required_status_str.split(',')
                if e.isdigit()
            ]

        webservice_configurator_str = config_parameter.get_param('webservice_configurator_ids', False)
        webservice_configuration_ids = []
        if webservice_configurator_str:
            webservice_configuration_ids = [
                int(e) for e in webservice_configurator_str.split(',')
                if e.isdigit()
            ]
        # tomamos todas las configuraciones para buscar las que coincidan con el parametro con el nombre de la configuracion solicitada
        configuratorWebService_ids = http.request.env['sincro_data.webservice_configurator'].browse(
            webservice_configuration_ids)

        # toammaos el parametro de la url
        param_config = params['config_name']

        selected_config = (configuratorWebService_ids.filtered(
            lambda config: str(config.name) == str(param_config)))

        # raw_json = self.getJsonFromConfig(selected_config.panel_configuration)
        # json_res = '{'+raw_json+'}';
        domain_data = self.compute_domain(selected_config.domain)
        data_items = http.request.env[selected_config.sudo().model_id.model].sudo().search(domain_data)

        # return self.cleaned_json(selected_config, adm_application_test[0])

        json_res = ''
        json_aux_res = '{"%s": [' % selected_config.label
        idx = 0
        for adm_aux in data_items:
            if idx > 0:
                json_aux_res += ','
            json_res = self.cleaned_json(selected_config, adm_aux);
            json_test = json.loads(json_res)
            json_aux_res += json.dumps(json_test[list(json_test.keys())[0]])
            idx += 1

        json_aux_res += ']}'

        # tomamos parametro que nos indica si queremos un formato comprimido (si solo tiene un elemento
        # dentro de un value del dictionario entonces toma ese valor y lo sube de nivel)
        # Example:
        # {"applid": {"FACTSid": {"FACTSid_inner": "False"}}} equivale a {"applid": {"FACTSid": "False"}}

        if 'pretty' in params:
            json_pretty = {}
            self.json_to_pretty_format(json.loads(json_res), json_pretty)
            return json.dumps(json_pretty)

        return json_aux_res
