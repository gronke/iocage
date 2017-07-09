import subprocess

class Command:

  def exec(self, command):

    if isinstance(command, str):
      command = [command]

    return subprocess.check_output(command, shell=False)
