class BridgeSet(set):

  def __init__(self, jail_config=None):
    self.jail_config = jail_config
    set.__init__(self)


  def add(self, value, notify=True):
    set.add(self, value)
    if notify:
      try:
        self.jail_config.update_special_property("interfaces")
      except:
        pass


  def remove(self, value, notify=True):
    set.remove(self, value)
    if notify:
      try:
        self.jail_config.update_special_property("interfaces")
      except:
        pass


class JailConfigInterfaces(dict):

  def __init__(self, value, jail_config=None):
    dict.__init__(self, {})
    dict.__setattr__(self, 'jail_config', jail_config)

    self.read(value)


  def read(self, value):
    tmp = {}
    nic_pairs = value.split(" ")
    for nic_pair in nic_pairs:
      jail_if, bridge_if = nic_pair.split(":", maxsplit=1)

      self.add(jail_if, bridge_if, notify=False)
      

  def add(self, jail_if, bridges=[], notify=True):

    if isinstance(bridges, str):
      bridges = [bridges]

    try:
      prop = dict.__getitem__(self, jail_if)
    except:
      prop = self.__empty_jail_if(jail_if)

    for bridge_if in bridges:
      prop.add(bridge_if, notify=False)

    if notify:
      self.__notify()


  def __setitem__(self, jail_if, bridges):
    
    try:
      dict.__delitem__(self, jail_if)
    except:
      pass

    self.add(jail_if, bridges)


  def __delitem__(self, jail_if):
    dict.__delitem__(self, jail_if)
    self.__notify()


  def __notify(self):
      try:
        self.jail_config.update_special_property("interfaces")
      except:
        pass


  def __empty_jail_if(self, jail_if):

    prop = BridgeSet(self.jail_config)
    dict.__setitem__(self, jail_if, prop)
    return prop

  def __str__(self):
    out = []
    for jail_if in self:
      for bridge_if in self[jail_if]:
        out.append(f"{jail_if}:{bridge_if}")
    return " ".join(out)
