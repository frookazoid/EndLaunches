
import colorama, json, threading
from classes.logger import logger
from classes.end import launch
from classes.creator import create

colorama.init()
log = logger().log


log("--------------------------", "gray")
log("End V.01", "yellow")
log("Developed by: Euphoria", "yellow")
log("--------------------------", "gray")

try:
    with open('./config/config.json') as json_data_file:
        config = json.load(json_data_file)
        log("Config Loaded", "lightpurple")
except:
    log("Error in config.json...", "error")
    quit()

try:
    with open('./config/proxies.json') as json_data_file:
        proxies = json.load(json_data_file)
        log("%s Proxy(s) Loaded" % len(proxies), "lightpurple")
except:
    log("Error in proxy file..", "error")
    quit()


try:
    with open('./config/accounts.txt') as f:
        accounts = f.read().splitlines()
        log("%s Account(s) Loaded" % len(accounts), "lightpurple")
except:
    log("Error in Accounts file..", "error")
    quit()

try:
    with open('./config/profiles.json') as json_data_file:
        profiles = json.load(json_data_file)
        log("%s Profile(s) Loaded" % len(profiles), "lightpurple")
except:
    log("Error in profiles file..", "error")
    quit()



log("--------------------------", "gray")

def main(x, proxies, config, accounts, profiles):
    EL = launch(x, proxies, config, accounts, profiles)
    EL.run()

def acc(x, proxies, config):
    EAC = create(x, proxies, config)
    EAC.run()



threads = []

if config['generator']['gen']:
    log("Account Generator Enabled", "info")
    log("--------------------------", "gray")
    for x in range(config['generator']['amount']):
        t = threading.Thread(target=acc, args=(x, proxies, config))
        threads.append(t)
        t.start()
else:
    for x in range(len(profiles)):
        t = threading.Thread(target=main, args=(x, proxies, config, accounts[x], profiles[x]))
        threads.append(t)
        t.start()