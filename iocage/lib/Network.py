import subprocess
from hashlib import md5
import re

class Network:

  def __init__(self, jail, nic="vnet0", mtu=1500):
    self.jail = jail
    self.nic = nic
    self.mtu = mtu


  def setup(self):
    
    self.__generate_mac_address_pair()
    epair_a, epair_b = self.__create_vnet_iface()

    self.__set_nic(epair_a, {
      "mtu": self.mtu,
      "name": self.nic_local_name
    })

    self.__set_nic(self.nic_local_name, {
      "link": self.mac_a,
      "description": self.nic_local_description
    })

    self.__set_nic(epair_b, {
      "vnet": self.jail.identifier
    })

    self.jail.exec(self.__get_nic_command(epair_b, {
      "link": self.mac_b
    }))


  @property
  def nic_local_name(self):
    self.jail.require_jail_running()

    return f"{self.nic}:{self.jail.jid}"


  @property
  def nic_local_description(self):
    return f"associated with jail: {self.jail.humanreadable_name}"


  def __set_nic(self, interface, properties):
    command = self.__get_nic_command(interface, properties)
    subprocess.check_output(command)


  def __get_nic_command(self, interface, properties):
    command = ["/sbin/ifconfig", interface]
    for key in properties:
      command.append(key)
      command.append(str(properties[key]))
    print(command)
    return (command)


  def __create_vnet_iface(self):
    epair_a_cmd = ["ifconfig", "epair", "create"]
    epair_a = subprocess.Popen(epair_a_cmd, stdout=subprocess.PIPE, shell=False).communicate()[0]
    epair_a = epair_a.decode("utf-8").strip()
    epair_b = f"{epair_a[:-1]}b"
    return epair_a, epair_b


  def __generate_mac_bytes(self):
    m = md5()
    m.update(self.jail.uuid.encode("utf-8"))
    m.update(self.nic.encode("utf-8"))
    prefix = self.jail.config.mac_prefix
    return f"{prefix}{m.hexdigest()[0:12-len(prefix)]}"


  def __generate_mac_address_pair(self):
    self.mac_a = self.__generate_mac_bytes()
    self.mac_b = hex(int(self.mac_a, 16) + 1)[2:].zfill(12)
