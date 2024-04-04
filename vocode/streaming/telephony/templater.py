import os
from jinja2 import Environment, FileSystemLoader
from fastapi import Response


class Templater:
    def __init__(self):
        self.templates = Environment(
            loader=FileSystemLoader("%s/templates/" % os.path.dirname(__file__))
        )

    def render_template(self, template_name: str, **kwargs):
        template = self.templates.get_template(template_name)
        return template.render(**kwargs)

    def get_connection_twiml(self, call_id: str, base_url: str):
        return Response(
            self.render_template("connect_call.xml", base_url=base_url, id=call_id),
            media_type="application/xml",
        )

    def update_twiml_connection_with_digits(self, call_id: str, base_url: str, digits: str):
        return Response(
            self.render_template("digits_update_call.xml", base_url=base_url, id=call_id, digits=digits),
            media_type="application/xml",
        )
    
    def update_twiml_connection_with_digits_to_string(self, call_id: str, base_url: str, digits: str):
        return self.render_template("digits_update_call.xml", base_url=base_url, id=call_id, digits=digits)
