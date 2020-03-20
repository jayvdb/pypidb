class Input(object):
    def __init__(self, value, source=None):
        self._value = value
        self.source = source

    def __str__(self):  # pragma: no cover
        return self.value + " @ " + (self.source or "Unknown")

    def __repr__(self):
        if self.source:
            return "{}({!r}) @ {}".format(
                self.__class__.__name__, self.value, self.source
            )
        return "{}({!r})".format(self.__class__.__name__, self.value)

    @property
    def value(self):
        return self._value


class Url(Input):
    pass


class UrlSet(Input):
    def __str__(self):
        return "{!r}".format(self.value)


class Email(Input):
    pass


class Name(Input):
    pass


class Text(Input):
    def __str__(self):
        return self.value[:10] + "..."

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, str(self))


class Webpage(Text):
    def __str__(self):  # pragma: no cover
        return self.value[:10] + "..."

    @property
    def value(self):
        assert self._value
        assert self._value.text
        return self._value.text
