# FIXME: This is currently a workaround. Instead of hardcoding these values we
#  should implement a way of loading configuration data from the environment or
#  a config file.
class AppConfig:
    name = "Karman API"
    debug = True


app_config = AppConfig()
