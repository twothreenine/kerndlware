import configparser

config = configparser.ConfigParser()
config.read('core/config.ini')

def get_config(attribute):
    global config
    return eval("config['CustomSettings']['"+attribute+"']")

def set_config(attribute, value):
    global config
    exec("config['CustomSettings']['"+attribute+"'] = value")
    with open('core/config.ini', 'w') as configfile:
        config.write(configfile)

def reset_config(attribute):
    global config
    exec("config['CustomSettings']['"+attribute+"'] = config['DefaultSettings']['"+attribute+"']")
    with open('core/config.ini', 'w') as configfile:
        config.write(configfile)