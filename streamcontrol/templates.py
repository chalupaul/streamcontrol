from dataclasses import dataclass
from os.path import dirname, join

from jinja2 import Environment, FileSystemLoader, select_autoescape

from streamcontrol.config import config


class TextTemplate(object):
    def __init__(self, template_name):
        app_basedir = dirname(__file__)
        template_dir = join(app_basedir, "_templates")
        if not template_name.endswith(".jinja"):
            template_name += ".jinja"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=select_autoescape()
        )
        self.template = self.jinja_env.get_template(template_name)

    def render(self, **kwargs):
        return self.template.render(**kwargs)

    def render_to_file(self, output_file, **kwargs):
        output_path = join(config.text_path, output_file)
        with open(output_path, "w+") as fp:
            text = self.render(**kwargs)
            fp.write(text)


@dataclass
class Templates:
    next_event: TextTemplate = TextTemplate("next_stream")
