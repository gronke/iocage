import libzfs
import subprocess

from iocage.lib.JailConfig import JailConfig
from iocage.lib.Network import Network

class Jail:

  def __init__(self, data = {}, root_dataset="zroot/iocage"):
    self.root_dataset = root_dataset
    self.zfs = libzfs.ZFS(history=True, history_prefix="<iocage>")
    self.config = JailConfig(data=data)
    self.networks = []

    try:
      self.config.dataset = self.dataset
      self.config.read()
    except:
      pass
    

  def start(self):
    self.require_jail_existing()
    self.require_jail_stopped()
    self._launch_jail()
    self._start_network()


  def exec(self, command):

    if isinstance(command, str):
      command = [command]

    stdout = subprocess.check_output(([
      "/usr/sbin/jexec",
      self.identifier
    ] + command), shell=False)
    return stdout


  def _launch_jail(self):


  def _start_network(self):

    nics = self.config.interfaces
    for nic in nics:
      net = Network(jail=self, nic=nics[nic])
      net.setup()


  def require_jail_existing(self):
    if not self.exists:
      raise Exception(f"Jail {self.humanreadable_name} does not exist")


  def require_jail_stopped(self):
    if self.running:
      raise Exception(f"Jail {self.humanreadable_name} is already running")


  def require_jail_running(self):
    if not self.running:
      raise Exception(f"Jail {self.humanreadable_name} is not running")


  def _get_humanreadable_name(self):
    try:
      return self.config.name
    except:
      pass

    try:
      return self.config.uuid
    except:
      pass

    raise "This Jail does not have any identifier yet"


  def _get_stopped(self):
    return self.running != True;


  def _get_running(self):
    return self.jid != None


  def _get_jid(self):
    try:
      child = subprocess.Popen([
        "/usr/sbin/jls",
        "-j",
        self.identifier,
        "-v",
        "jid"
      ], shell=False, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
      return child.stdout.read(1).decode("utf-8").strip()
    except:
      return None


  def _get_identifier(self):
    return f"ioc-{self.uuid}"


  def _get_exists(self):
    try:
      self.dataset
      return True
    except:
      return False


  def _get_uuid(self):
    return self.config.uuid


  def _get_dataset_name(self):
    return f"{self.root_dataset}/jails/{self.config.uuid}"


  def _get_dataset(self):
    return self.zfs.get_dataset(self._get_dataset_name())


  def _get_path(self):
    return self.dataset.mountpoint


  def _get_logfile_path(self):
    return f"{self.root_dataset.mountpoint}/log/{self.identifier}.log"


  def __getattr__(self, key):
    try:
      method = self.__getattribute__(f"_get_{key}")
      return method()
    except:
      raise Exception(f"Jail property {key} not found")
