class NagiosResponse:
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self):
        self._code = self.OK
        self._status = ["OK", "WARNING", "CRITICAL", "UNKNOWN"]
        self._ok_msg = "XML is valid."
        self._warning_msg = ""
        self._critical_msg = ""
        self._unknown_msg = ""

    def _add_prefix(self, msg):
        return f"{self._status[self._code]} - {msg}"

    def _create_ok_msg(self, msg):
        self._ok_msg = "{}\n{}".format(self._ok_msg, msg.strip()).strip()

    def _create_warning_msg(self, msg):
        self._warning_msg = f"{self._warning_msg}\n{msg}".strip()

    def _create_critical_msg(self, msg):
        self._critical_msg = f"{self._critical_msg}\n{msg}".strip()

    def _create_unknown_msg(self, msg):
        self._unknown_msg = f"{self._unknown_msg}\n{msg}".strip()

    def _set_code(self, code):
        if self._code == self.UNKNOWN:
            pass

        elif self._code == self.CRITICAL:
            if code == self.UNKNOWN:
                self._code = self.UNKNOWN

        elif self._code == self.WARNING:
            if code in [self.UNKNOWN, self.CRITICAL]:
                self._code = code

        else:
            self._code = code

    def set_ok(self, msg=""):
        self._set_code(self.OK)
        self._create_ok_msg(msg)

    def set_warning(self, msg=""):
        self._set_code(self.WARNING)
        self._create_warning_msg(msg)

    def set_critical(self, msg=""):
        self._set_code(self.CRITICAL)
        self._create_critical_msg(msg)

    def set_unknown(self, msg=""):
        self._set_code(self.UNKNOWN)
        self._create_unknown_msg(msg)

    def get_code(self):
        return self._code

    def get_message(self):
        if self._code == self.OK:
            return self._add_prefix(self._ok_msg)

        if self._code == self.WARNING:
            return self._add_prefix(self._warning_msg)

        if self._code == self.CRITICAL:
            return self._add_prefix(self._critical_msg)

        if self._code == self.UNKNOWN:
            return self._add_prefix(self._unknown_msg)
