'''
Created on Jan 13, 2014
@author: Eugene Syriani
@version: 0.2.5

This is module represents the settings for BiBler.
@group Enumerations: BibStyle, ExportFormat, ImportFormat
'''

import os
import utils

class ImportFormat:
    """
    Enumerates the allowed import formats.
    """
    BIBTEX = 'bib'
    """
    .bib extension representing a BibTeX file.
    """
    CSV = 'csv'
    """
    .csv extension representing a Comma-Separated Values file.
    """

class ExportFormat:
    """
    Enumerates the allowed export formats.
    """
    BIBTEX = 'bib'
    """
    .bib extension representing a BibTeX file.
    """
    CSV = 'csv'
    """
    .csv extension representing a Comma-Separated Values file.
    """
    HTML = 'html'

class BibStyle:
    """
    Enumerates the possible bibliography styles.
    """
    ACM = 'acm'
    IEEE = 'ieee'

class Preferences(object):
    """
    Holds the preferences of this BiBler instance, such as:
    the bibliography style and the default directory.
    """
    __metaclass__ = utils.Singleton
    def __init__(self):
        self.bibStyle = BibStyle.ACM
        self.defaultDir = os.path.pardir