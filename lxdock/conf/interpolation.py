from string import Template


def interpolate_variables(config_dict, mapping):
    """ Performs variable interpolation in the considered config.

    :param config_dict: dictionary containing the configuration values
    :param mapping: dictionary containing the available variables
    :type arg1: dict
    :type arg1: dict
    :return: dictionary containing the interpolated config
    :rtype: dict
    """
    def interpolate(value):
        if isinstance(value, str):
            return Template(value).substitute(**mapping)
        elif isinstance(value, dict):
            return {k: interpolate(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [interpolate(v) for v in value]
        return value

    return {k: interpolate(v) for k, v in config_dict.items()}
