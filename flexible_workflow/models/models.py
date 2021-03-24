# -*- coding: utf-8 -*-

import json
from lxml import etree

from odoo import models, api, fields

class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def fields_view_get(self, view_id=None, view_type="form", toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == "form":
            workflow_obj = self.env["workflow.workflow"]
            workflow = workflow_obj.search([("model_id","=",self.env["ir.model"]._get(self._name).id)])
            if not workflow:
                return res
            doc = etree.XML(res["arch"])
            for stage in workflow.stage_ids:
                for attribute in stage.attribute_ids:
                    nodes = doc.xpath(attribute.expression)
                    for node in nodes:
                        modifiers = {}
                        if node.get("modifiers"):
                            modifiers = json.loads((node.get("modifiers")))
                        if "invisible" in modifiers and isinstance(modifiers["invisible"], list):
                            modifiers["invisible"] =  ["|"]  + modifiers["invisible"]
                        else:
                            modifiers["invisible"] = []
                        modifiers["invisible"].append(("workflow_stage_id","=",stage.id))
                        node.set("modifiers", json.dumps(modifiers))
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res