from iocage.lib.JailConfigJSON import JailConfigJSON
from iocage.lib.JailConfigZFS import JailConfigZFS
from iocage.lib.JailConfigInterfaces import JailConfigInterfaces

import uuid

class JailConfig(JailConfigJSON, JailConfigZFS):

  def __init__(self, data = {}):

    object.__setattr__(self, 'data', {})
    object.__setattr__(self, 'dataset', None)
    object.__setattr__(self, 'special_properties', {})

    # the UUID is used in many other variables and needs to be set first
    try:
      self._set_uuid(data.uuid)
    except:
      pass

    # be aware of iocage-legacy jails for migration
    try:
      self.legacy = data.legacy == True
    except:
      self.legacy = False

    self.clone(data);


  def clone(self, data):
    for key in data:
      self.__setattr__(key, data[key])


  def update_special_property(self, name):
    self.data[name] = str(self.special_properties[name])


  def _set_name(self, value):

    self.name = value

    try:
      self.host_hostname
    except:
      print(f"Setting host_hostname as well to {value}")
      self.host_hostname = value
      pass


  def save(self):
    JailConfigJSON.save(self)
    JailConfigZFS.save(self)


  def _set_uuid(self, uuid):
      self.uuid = UUID(uuid)


  def __get_ip_addr(self, config_line):
    
    out = {}

    ip_addresses = config_line.split(" ")
    for ip_address_string in ip_addresses:
      
      nic, address = ip_address_string.split("|", maxsplit=1)
      
      try:
        out[nic]
      except:
        out[nic] = []
        pass

      out[nic].append(address)

    return out


  def _get_ip4_addr(self):
    return self.__get_ip_addr(self.data["ip4_addr"])
    

  def _get_ip6_addr(self):
    return self.__get_ip_addr(self.data["ip6_addr"])


  def _get_interfaces(self):
    return self.special_properties["interfaces"]
    

  def _set_interfaces(self, value):
    self.special_properties["interfaces"] = JailConfigInterfaces(value, jail_config=self)
    self.update_special_property("interfaces")


  def _default_mac_prefix():
    return "02ff60"


  def __getattr__(self, key):

    # passthrough existing properties
    try:
      return self.__getattribute__(key)
    except:
      pass

    # data with mappings
    try:
      get_method = self.__getattribute__(f"_get_{key}")
      return get_method()
    except:
      if(key == "interfaces"):
        raise
      pass

    # plain data attribute
    try:
      return self.data[key]
    except:
      pass

    # then fall back to default
    try:
      fallback_method = self.__getattribute__(f"_default_{key}")
      return fallback_method()
    except:
      raise Exception(f"Variable {key} not found")


  def __setattr__(self, key, value):

    # passthrough existing properties
    try:
      self.__getattribute__(key)
      object.__setattr__(self, key, value)
      return
    except:
      pass

    try:
      setter_method = self.__getattribute__(f"_set_{key}")
      setter_method(value)
    except:
      self.data[key] = value
      pass

  def __str__(self):
    return JailConfigJSON.toJSON(self)
