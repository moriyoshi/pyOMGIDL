from unittest import TestSuite, defaultTestLoader

__all__ = [
    'suite',
    ]

def suite():
    return defaultTestLoader.loadTestsFromName('pyomgidl.reader.tests')
