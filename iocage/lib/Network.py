import subprocess as su
from hashlib import md5

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
        "link": mac_a,
        "description": self.nic_local_description
      })

    self.__set_nic(epair_b, {
        "vnet": f"ioc-{self.jail.uuid}"
      })

    self.jexec(self._get_nic_command(epair_b, {
        "link": mac_b
      }))

  @property
  def nic_local_name(self):
    return "{self.nic}:{self.jid}"

  @property
  def nic_local_description(self):
    return f"associated with jail: {self.jail.humanreadable_name}"

  def __set_nic(self, interface, properties):
    for key in properties:
      command = self.__get_nic_command(interface, properties)
      return
      
      try:
        out = subprocess.check_output(command)
        out = out.decide("utf-8")
      except su.CalledProcessError:
        raise

  def __get_nic_command(self, interface, properties):
    out = ["ifconfig", interface]
    for key in properties:
      out.append(key)
      out.append(properties[key])
    print(out)
    return " ".join(out)


  def __create_vnet_iface():
    epair_a_cmd = ["ifconfig", "epair", "create"]
    epair_a = su.Popen(epair_a_cmd, stdout=su.PIPE, shell=False).communicate()[0]
    epair_a = epair_a.strip()
    epair_b = re.sub(b"a$", b"b", epair_a)
    return epair_a, epair_b


  def __generate_mac_bytes(self):
    m = md5()
    m.update(self.jail.uuid.encode("utf-8"))
    m.update(self.nic.encode("utf-8"))
    prefix = self.get("mac_prefix")
    return f"{prefix}{m.hexdigest()[0:12-len(prefix)]}"


  def __generate_mac_address_pair(self):
    self.mac_a = self.__generate_mac_bytes()
    self.mac_b = hex(int(mac_a, 16) + 1)[2:].zfill(12)
