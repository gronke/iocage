import libzfs

import iocage.lib.JailConfig

class Jail:

  def __init__(self, data = {}, iocroot="/iocage"):
    self.iocroot = iocroot
    self.zfs = libzfs.ZFS(history=True, history_prefix="<iocage>")
    self.config = JailConfig(data=data, zfs=self.zfs)
    
    try:
      if self.exists:
        self.config.read_json(f"{self.path}/config.json")
    except:
      # ToDo
      raise "Maybe this is a iocage-legacy jail that needs to be migrated"


  def start(self):
    self.__require_existing_jail(self)




  def __require_existing_jail(self):
    if not self.exists:
      raise "Jail {self.humanreadable_name} does not exist"


  def __get_humanreadable_name(self):
    try:
      return self.config.name
    except:
      pass

    try:
      return self.config.uuid
    except:
      pass

    raise "This Jail does not have any identifier yet"


  def __get_exists(self):
    try:
      self.dataset
      return True
    except:
      return False


  def __get_dataset_name(self):
    return f"{self.pool}/jails/{self.config.uuid}"


  def __get_dataset(self):
    return self.zfs.get_dataset(self.__get_dataset_name())


  def __get_path(self):
    return self.dataset.mountpoint


  def __get_jail_root(self):
    jail_path = self.__get_jail_path()
    return f"{jail_path}/root"


  def __getattr__(self, key):
    try:
      method = self[f"__get_{key}"]
      return method()
    except:
      raise Exception(f"Variable {key} not found")
