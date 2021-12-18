# FIXME: This is currently a workaround. Instead of hardcoding these values we
#  should implement a way of loading configuration data from the environment or
#  a config file.
class AppConfig:
    name = "Karman API"
    debug = True

    oauth2_path = "oauth2"
    oauth2_password_endpoint = "login"


app_config = AppConfig()
