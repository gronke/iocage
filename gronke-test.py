import time
from iocage.lib.Jails import Jails
from iocage.lib.Jail import Jail

uuid = "32101588-868f-4c1b-9e14-19a0ab7af04a"
print(f"Starting Jail {uuid}")

start_time = time.time()
j = Jail({ "uuid": uuid })
j.start()
end_time = time.time()

print(f"Jail started with JID {j.jid}")
print("--- %s seconds ---" % (time.time() - start_time))

#start_time = time.time()
#jail_list = Jails().list()
#for jail in jail_list:
#  print(f"UUID={jail.uuid} JID={jail.jid} TAG={jail.config.tag}")
#end_time = time.time()
#print("--- %s seconds ---" % (time.time() - start_time))

