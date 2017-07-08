from iocage.lib.JailConfigJSON import JailConfigJSON
from iocage.lib.JailConfigZFS import JailConfigZFS

import uuid

class JailConfig(JailConfigJSON, JailConfigZFS):

  def __init__(self, data = {}, dataset = None):

    self.data = [];
    self.uuid = None

    # the UUID is used in many other variables and needs to be set first
    try:
      self.__set_uuid(data.uuid)
    except:
      pass

    # be aware of iocage-legacy jails for migration
    try:
      self.legacy = data.legacy == True
    except:
      self.legacy = False

    # when a dataset is passed, try to read config.json
    self.dataset = None
    try:
      self.dataset = dataset
      JailConfigJSON.read(self)
    except:
      # ToDO maybe a iocage-legacy jail
      pass

    self.clone(data);


  def clone(self, data):

    for key, value in data:
      this[key] = data


  def __set_name(self, value):

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


  def __set_uuid(self, uuid):
      self.uuid = UUID(uuid)

  def __getattr__(self, key):

    # look if the attribute already exists
    try:
      return self.data[key]
    except:
      pass

    # then fall back to default
    try:
      fallback_method = self[f"__default_{key}"]
      return fallback_method()
    except:
      raise Exception(f"Variable {key} not found")


  def __setattr__(self, key, value):

    try:
      object.__setattr__(self, key, value)
      return
    except:
      pass
    
    try:
      setter_method = self[f"__set_{key}"]
      setter_method(value)
    except:
      self.data[key] = value
