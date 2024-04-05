from dataclasses import dataclass

from lk_plants.core.taxonomy.Phylum import Phylum
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Classis(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Phylum
