import subprocess
from hashlib import md5
import re

from iocage.lib.NetworkInterface import NetworkInterface

class Network:

  def __init__(self, jail, nic="vnet0", mtu=1500):
    self.vnet = True
    self.jail = jail
    self.nic = nic
    self.mtu = mtu

  def setup(self):
    if self.vnet:  
      jail_if, host_if = self.__create_vnet_iface()


  @property
  def nic_local_name(self):
    self.jail.require_jail_running()

    return f"{self.nic}:{self.jail.jid}"


  @property
  def nic_local_description(self):
    return f"associated with jail: {self.jail.humanreadable_name}"  


  def __create_vnet_iface(self):

    # create new epair interface
    epair_a_cmd = ["ifconfig", "epair", "create"]
    epair_a = subprocess.Popen(epair_a_cmd, stdout=subprocess.PIPE, shell=False).communicate()[0]
    epair_a = epair_a.decode("utf-8").strip()
    epair_b = f"{epair_a[:-1]}b"

    mac_a, mac_b = self.__generate_mac_address_pair()

    host_if = NetworkInterface(
      name=epair_a,
      mac=mac_a,
      mtu=self.mtu,
      description=self.nic_local_description,
      rename=self.nic_local_name
    )

    # assign epair_b to jail
    self.__assign_vnet_iface_to_jail(epair_b, self.jail.identifier)

    jail_if = NetworkInterface(
      name=epair_b,
      mac=mac_b,
      mtu=self.mtu,
      rename=self.nic,
      jail=self.jail
    )

    return jail_if, host_if


  def __assign_vnet_iface_to_jail(self, nic, jail_name):
    NetworkInterface(
      name=nic,
      vnet=jail_name
    )


  def __generate_mac_bytes(self):
    m = md5()
    m.update(self.jail.uuid.encode("utf-8"))
    m.update(self.nic.encode("utf-8"))
    prefix = self.jail.config.mac_prefix
    return f"{prefix}{m.hexdigest()[0:12-len(prefix)]}"


  def __generate_mac_address_pair(self):
    mac_a = self.__generate_mac_bytes()
    mac_b = hex(int(self.mac_a, 16) + 1)[2:].zfill(12)
    return mac_a, mac_b
