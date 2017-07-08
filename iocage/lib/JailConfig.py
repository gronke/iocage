from iocage.lib.JailConfigJSON import JailConfigJSON
from iocage.lib.JailConfigZFS import JailConfigZFS

import uuid

class JailConfig(JailConfigJSON, JailConfigZFS):

  data = {}
  dataset = None

  def __init__(self, data = {}):

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


  def _get_interfaces(self):
    out = {}
    nic_pairs = self.data["interfaces"].split(" ")
    for nic_pair in nic_pairs:
      jail_if, bridge_if = nic_pair.split(":")
      out[jail_if] = bridge_if
    return out

  def _set_interfaces(self, value):

    if not isinstance(value, str):
      tmp = []
      for jail_if in value:
        bridge_if = value[jail_if]
        tmp.append(f"{jail_if}:{bridge_if}")
      value = " ".join(tmp)
      del tmp

    self.data["interfaces"] = value

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

  def toJSON(self):
    return JailConfigJSON.toJSON(self)
