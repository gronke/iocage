from iocage.lib.Command import Command

class NetworkInterface:

  ifconfig_command: "/sbin/ifconfig"

  def __init__(self, name="vnet0", ipv4=[], ipv6=[], mac=None, mtu="auto", description=None, rename=None, jail=None):

    self.jail = jail

    self.name = name
    self.ipv4 = ipv4
    self.ipv6 = ipv6

    self.settings = {}

    if mac != None:
      self.settings["link"] = self.mac

    if mtu != None:
      self.settings["mtu"] = self.mtu

    if description != None:
      self.settings["description"] = self.description

    if vnet != None:
      self.settings["vnet"] = self.vnet

    # rename interface when applying settings next time
    if isinstance(rename, str):
      self.rename = True
      self.settings["name"] = rename
    else:
      self.rename = False


  def apply(self):
    self.apply_settings()
    self.apply_addresses()
    

  def apply_settings(self):
    command = [self.ifconfig_command, self.name]
    for key in self.settings:
      command.append(key)
      command.append(self.settings[key])
    self.exec(command)

    # update name when the interface was renamed
    if self.rename:
      self.name = self.settings["rename"]
      del self.settings["rename"]
      self.rename = False


  def apply_addresses(self):
    self.__apply_addresses(self.ipv4, ipv6=False)
    self.__apply_addresses(self.ipv6, ipv6=True)


  def __apply_addresses(self, addresses, ipv6=False):
    family = "inet6" if ipv6 else "inet"
    for address in addresses:
      command = [self.ifconfig_command, self.name, family, address]
      self.exec(command)


  def exec(self, command, force_local=False):
    if self.__is_jail():
      return self.jail.exec(command)
    else:
      return Command.exec(self, command)


  def __is_jail(self):
    return isinstance(self.jail, Jail)
