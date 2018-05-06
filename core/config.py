import configparser

config = configparser.ConfigParser(interpolation=None)
config.read('core/config.ini')

def get_config(attribute):
    global config
    return eval("config['CustomSettings']['"+attribute+"']")

def get_boolean_config(attribute):
    global config
    boolean = eval("config['CustomSettings']['"+attribute+"']")
    if boolean == "enabled":
        return True
    else:
        return False

def set_config(attribute, value):
    global config
    exec("config['CustomSettings']['"+attribute+"'] = value")
    with open('core/config.ini', 'w') as configfile:
        config.write(configfile)

def set_boolean_config(attribute, value):
    global config
    if value == True:
        exec("config['CustomSettings']['"+attribute+"'] = 'enabled'")
    else:
        exec("config['CustomSettings']['"+attribute+"'] = 'disabled'")
    with open('core/config.ini', 'w') as configfile:
        config.write(configfile)

def reset_config(attribute):
    global config
    exec("config['CustomSettings']['"+attribute+"'] = config['DefaultSettings']['"+attribute+"']")
    with open('core/config.ini', 'w') as configfile:
        config.write(configfile)