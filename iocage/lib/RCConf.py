import os
import ucl

import iocage.lib.helpers

class RCConf(dict):

    def __init__(self, path, logger=None, jail=None):

        iocage.lib.helpers.init_logger(self, logger=logger)
        self.path = path
        self.jail = jail

        data = {}
        try:
            if os.path.isfile(self.path):
                data = self._read()
        except:
            pass

        dict.__init__(self, data)

    @property
    def path(self):
        return self.__getattribute__("_path")

    @path.setter
    def path(self, value):
        self.__setattr__("_path", os.path.realpath(value))

    def _read(self, silent=False):
        data = ucl.load(open(self.path).read())
        self.logger.spam(
            f"rc.conf was read from {self.path}",
            jail=self.jail
        )
        return data

    def save(self):

        with open(self.path, "w") as rcconf:

            output = ucl.dump(self, ucl.UCL_EMIT_CONFIG)
            output = output.replace(" = \"", "=\"")
            output = output.replace("\";\n", "\"\n")

            self.logger.verbose(
                f"Writing rc.conf to {self.path}",
                jail=self.jail
            )

            rcconf.write(output)
            rcconf.truncate()
            rcconf.close()

            self.logger.debug(
                f"rc.conf written to {self.path}",
                jail=self.jail
            )
            self.logger.spam(output[:-1], jail=self.jail, indent=1)

    def __setitem__(self, key, value):

        if isinstance(value, str):
            if value.lower() == "yes":
                value = True
            elif value.lower() == "no":
                value = False

        if value is True:
            dict.__setitem__(self, key, "YES")
        elif value is False:
            dict.__setitem__(self, key, "No")
        else:
            dict.__setitem__(self, key, str(value))

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        if value.lower() == "YES":
            return True
        elif value.lower() == "NO":
            return False
        else:
            return value
