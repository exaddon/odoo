# Copyright (C) 2017 Creu Blanca
# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import logging

from werkzeug.urls import url_decode

from odoo.http import (
    content_disposition,
    request,
    route,
    serialize_exception as _serialize_exception,
)
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers.report import ReportController

_logger = logging.getLogger(__name__)


class ReportController(ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == "xlsx":
            report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(",")]
            if data.get("options"):
                data.update(json.loads(data.pop("options")))
            if data.get("context"):
                data["context"] = json.loads(data["context"])
                context.update(data["context"])
            xlsx = report.with_context(**context)._render_xlsx(
                reportname, docids, data=data
            )[0]
            xlsxhttpheaders = [
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet",
                ),
                ("Content-Length", len(xlsx)),
            ]
            return request.make_response(xlsx, headers=xlsxhttpheaders)
        return super().report_routes(reportname, docids, converter, **data)

    @route()
    def report_download(self, data, context=None, token=None):
        requestcontent = json.loads(data)
        print("requestcontent==============",requestcontent)
        url, report_type = requestcontent[0], requestcontent[1]
        if report_type == "xlsx":
            try:
                reportname = url.split("/report/xlsx/")[1].split("?")[0]
                print("reportname=============",reportname)
                docids = None
                print("docids=================",docids)
                if "/" in reportname:
                    reportname, docids = reportname.split("/")
                    print("reportname==============")
                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter="xlsx", context=context
                    )
                    print("response=======================",response)
                else:
                    # Particular report:
                    data = dict(
                        url_decode(url.split("?")[1]).items()
                    )  # decoding the args represented in JSON
                    print("data========================",data)
                    if "context" in data:
                        context, data_context = json.loads(context or "{}"), json.loads(
                            data.pop("context")
                        )
                        context = json.dumps({**context, **data_context})
                        print("context======================",context)
                    response = self.report_routes(
                        reportname, converter="xlsx", context=context, **data
                    )
                    print("response=======================",response)

                report = request.env["ir.actions.report"]._get_report_from_name(
                    reportname
                )
                print("report===================",report)
                filename = "%s.%s" % (report.name, "xlsx")
                print("filename======================",filename)

                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    print("ids========================",ids)
                    obj = request.env[report.model].browse(ids)
                    print("obj==================",obj)
                    if report.print_report_name and not len(obj) > 1:
                        report_name = safe_eval(
                            report.print_report_name, {"object": obj, "time": time}
                        )
                        print("report_name==============",report_name)
                        filename = "%s.%s" % (report_name, "xlsx")
                        print("filename==============",filename)
                if not response.headers.get("Content-Disposition"):
                    response.headers.add(
                        "Content-Disposition", content_disposition(filename)
                    )
                return response
            except Exception as e:
                _logger.exception("Error while generating report %s", reportname)
                se = _serialize_exception(e)
                error = {"code": 200, "message": "Odoo Server Error", "data": se}
                return request.make_response(html_escape(json.dumps(error)))
        else:
            return super().report_download(data, context=context, token=token)
