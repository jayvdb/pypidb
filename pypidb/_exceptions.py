class InvalidPackage(ValueError):
    pass


class InvalidPackageVersion(InvalidPackage):
    pass


class UnrecognisedStdlibBackport(InvalidPackage):
    pass


class IncompletePackageMetadata(ValueError):
    pass


class PackageWithoutFiles(IncompletePackageMetadata):
    pass


class PackageWithoutUrls(IncompletePackageMetadata):
    pass
