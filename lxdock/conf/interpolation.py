import re
from string import Template


class ConfigTemplate(Template):
    """ Like string.Template except that only variables in the format
    ${var} are supported but not the unbraced format of $var.

    The stricter format allows $ characters to be used more easily in
    the lxdock.yml file without having to escape them.
    """
    pattern = r"""
    %(delim)s(?:
      {(?P<braced>%(id)s)}  |  # delimiter and a braced identifier
      {(?P<named>%(id)s)}   |  # delimiter and a Python identifier (not needed)
      (?P<escaped>)         |  # Escape sequence (not needed)
      (?P<invalid>)            # Other ill-formed delimiter exprs
    )
    """ % dict(delim=re.escape(Template.delimiter), id=Template.idpattern)


def interpolate_variables(config_dict, mapping):
    """ Performs variable interpolation in the considered config.

    :param config_dict: dictionary containing the configuration values
    :param mapping: dictionary containing the available variables
    :type config_dict: dict
    :type mapping: dict
    :return: dictionary containing the interpolated config
    :rtype: dict
    """
    def interpolate(value):
        if isinstance(value, str):
            return ConfigTemplate(value).substitute(**mapping)
        elif isinstance(value, dict):
            return {k: interpolate(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [interpolate(v) for v in value]
        return value

    return {k: interpolate(v) for k, v in config_dict.items()}
