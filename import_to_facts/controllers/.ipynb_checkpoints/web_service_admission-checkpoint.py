import json

from formiodata.components import selectboxesComponent

from odoo import http
import datetime
import logging
# Se añaden campos:
# - Siblings
# - Datos de los hermanos
# - Horario de partner
# - Comment en res.parthner

# Updated 2020/12/14
# By Luis
# Just some clean up
_logger = logging.getLogger(__name__)

class AdmisionController(http.Controller):
    """ Controlador encargado de devolver datos de las admisiones,
    para insertarlas en FACTS
    """

    # devuelve formato pretty del JSON
    def json_to_pretty_format(self, json_data):

        for key,item in json_data.items():
            aux_json[key] = item

        return aux_json

    # devuelve la información en formato json dependiendo de la configuracion del webservice
    def get_json_from_config(self, value, data):
        result = ''
        if not value.fields:
            result += '"%s": "%s",' % (value.alias_field, data)
        else:
            result += '"%s":{' % value.alias_field
            for item in value.fields:
                if len(data) > 1:
                    result = result[0: -1] + '[{'
                for item_data in data:
                    result += self.get_json_from_config(item, item_data[item.field_id.sudo().name])
                    if len(data) > 1:
                        if result[-1] == ',':
                            result = result[0: -1]
                        result += '},{'
                if len(data) > 1:
                    result = result[0: -2] + ']'
            if result[-1] == ',':
                result = result[0: -1]
            if result[-1] != ']':
                result += '}'
            result += ','
        return result
        # csrf: hay que añadir este parametro siu es POST, PUT, etc, para todo

    # # devuelve la información en formato json dependiendo de la configuracion del webservice
    # def getJsonFromConfig(self, value, data):
    #     result = ''
    #     if not value.fields:
    #         result += '"%s": "%s",' % (value.alias_field, data)
    #     else:
    #         result += '"%s":{' % value.alias_field
    #         for item in value.fields:
    #             result += self.getJsonFromConfig(item, data[item.field_id.name])
    #         if result[-1] == ',':
    #             result = result[0: -1]
    #         result += '},'
    #     return result
    #     # csrf: hay que añadir este parametro siu es POST, PUT, etc, para todo

    def cleaned_json(self, value, appl):
        raw_res = self.get_json_from_config(value.panel_configuration, appl)
        if raw_res[-1] == ',':
            raw_res = raw_res[0: -1]
        if raw_res[-2::] == '}]':
            raw_res += '}'
        json_res = '{' + raw_res + '}';
        return json_res

    # menos para GET.
    @http.route("/import_to_facts/getAdmissions", auth="public", methods=["GET"], cors='*')
    def get_adm_uni(self, **params):
        
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

        webservice_configurator_str = config_parameter.get_param('adm_application_webservice_configurator_ids', False)
        webservice_configuration_ids = []
        if webservice_configurator_str:
            webservice_configuration_ids = [
                int(e) for e in webservice_configurator_str.split(',')
                if e.isdigit()
            ]
        # tomamos todas las configuraciones para buscar las que coincidan con el parametro con el nombre de la configuracion solicitada
        configuratorWebService_ids = http.request.env['import_to_facts.webservice_configurator'].browse(
            webservice_configuration_ids)

        # toammaos el parametro de la url
        param_config = params['config_name']

        selected_config = (configuratorWebService_ids.filtered(
            lambda config: str(config.name) == str(param_config)))

        # raw_json = self.getJsonFromConfig(selected_config.panel_configuration)
        # json_res = '{'+raw_json+'}';

        adm_application_test = http.request.env['adm.application'].sudo().browse([9,13])
        json_res=''
        json_aux_res = '{"applications": ['
        idx = 0
        for adm_aux in adm_application_test:
            if idx > 0:
                json_aux_res += ','
            json_res = self.cleaned_json(selected_config, adm_aux);
            json_test = json.loads(json_res)
            json_aux_res += json.dumps(json_test["appAdm"])
            idx += 1
            
        json_aux_res += ']}'
        
        # tomamos parametro que nos indica si queremos un formato comprimido (si solo tiene un elemento
        # dentro de un value del dictionario entonces toma ese valor y lo sube de nivel)
        # Example:
        # {"applid": {"FACTSid": {"FACTSid_inner": "False"}}} equivale a {"applid": {"FACTSid": "False"}}
        if 'pretty' in params:
            json_pretty ={}
            self.json_to_pretty_format(json.loads(json_res),json_pretty)
            return json.dumps(json_pretty)

        import_field = http.request.env['import_to_facts.import_field'].sudo()
        application_values = []
        alias_fields = {}

        if field_ids:
            list_field = field_ids.split(',')
            for data in list_field:
                application_values.append(import_field.browse(int(data)).field_id.name)
                alias_fields[import_field.browse(int(data)).field_id.name] = import_field.browse(int(data)).alias_field

        # DATOS DE LA APPLICATION
        # Crea una variable con el modelo desde donde se va a tomar la
        # información
        ApplicationEnv = http.request.env['adm.application'].sudo()

        # filtro del modelo: status = done y el checkBox Imported = False
        # search_domain = [("status_id.type_id", "in", ["done", "stage"])]
        search_domain = [("status_id", "in", required_status_ids)]

        # Tomar informacion basado en el modelo y en el domain IDS
        application_record = ApplicationEnv.search(search_domain, limit=10)

        application_values = application_record.read(application_values)
        # application_values = (http.request.env['res.partner'].sudo().search(search_domain,limit=1)).read(application_values)
        application_values_resp = []
        for app_value in application_values:
            aux_item = {}
            for k, v in app_value.items():
                key = k
                if k in alias_fields:
                    key = alias_fields[k]
                if isinstance(v, datetime.date):
                    aux_item[key] = v.strftime('%Y-%m-%d')
                else:
                    aux_item[key] = v
                    
            application_values_resp.append(aux_item)

        return json_aux_res

    @http.route("/admission/adm_insertId", auth="public", methods=["POST"],
                cors='*', csrf=False)
    # define una funcion principal 
    def insert_id(self, **kw):
        data = json.loads(kw["data"])
        for itemData in data:
            # itemData["odooId"]
            # itemData["factsId"]
            application = http.request.env['res.partner'].sudo()

            # Con browse podemos buscar todo un array un array y juntamos
            #  las lineas de arriba y lade abajo que estan comentadas
            application_record = application.browse([itemData["odooId"]])

            # Obtienes la información basada en los ids anteriores y tomando
            # en cuenta los campos definifos en la funcion posterior
            # application_values = application_record.partner_id

            # Cambiamos application_values por application_record debido al
            # cambio de la linea 294
            application_record.write({
                'facts_id': itemData["factsId"]
            })

        return json.dumps(data)
