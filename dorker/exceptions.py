class DorkerError(Exception):
    exit_code = 1


class ConfigError(DorkerError):
    exit_code = 2


class InputError(DorkerError):
    exit_code = 2


class NoKeysError(DorkerError):
    exit_code = 2


class NetworkError(DorkerError):
    exit_code = 3
