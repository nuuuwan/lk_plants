import os
from dataclasses import dataclass
from functools import cache, cached_property

from lk_plants.core.misc.NameTranslator import NameTranslator
from lk_plants.core.taxonomy.Genus import Genus
from lk_plants.core.taxonomy.taxon.Taxon import Taxon


@dataclass
class Species(Taxon):
    gbif_id: str
    powo_id: str
    iucn_id: str
    iucn_category: str
    common_names: list[str]

    def __hash__(self):
        return hash(self.__class__.__name__ + '.' + self.name)

    @property
    def genus(self):
        return self.parent

    @property
    def family(self):
        return self.genus.family

    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            authorship=self.authorship,
            parent_name=self.parent.name,
            #
            gbif_id=self.gbif_id,
            powo_id=self.powo_id,
            iucn_id=self.iucn_id,
            iucn_category=self.iucn_category,
            common_names=self.common_names,
        )

    @staticmethod
    def from_dict(d):
        parent = None
        needs_update = False
        if 'parent_name' in d:
            parent = Genus.from_name(d['parent_name'])
        elif 'genus_name' in d:
            parent = Genus.from_name(d['genus_name'])
            needs_update = True

        species = Species(
            name=d['name'],
            authorship=d['authorship'],
            parent=parent,
            #
            gbif_id=d['gbif_id'],
            powo_id=d['powo_id'],
            iucn_id=d['iucn_id'],
            iucn_category=d['iucn_category'],
            common_names=d['common_names'],
        )
        if needs_update:
            species.write(force=True)
        return species

    @staticmethod
    def from_plant_net_raw_result(d: dict) -> 'Species':
        d_species = d['species']
        name = Taxon.clean_name(d_species['scientificNameWithoutAuthor'])
        data_path = Species.get_data_path(name)
        if os.path.exists(data_path):
            return Species.from_name(name)
        genus = Genus.from_plant_net_raw_result(d)
        common_names = d_species.get('commonNames', [])

        def get_attr(d, k1, k2):
            v1 = d.get(k1, {})
            if not v1:
                return None
            return v1.get(k2, None)

        common_names2 = NameTranslator().get_common_names(name)
        combined_common_names = sorted(
            list(set(common_names + common_names2))
        )
        species = Species(
            name=name,
            authorship=d_species['scientificNameAuthorship'],
            parent=genus,
            gbif_id=get_attr(d, 'gbif', 'id'),
            powo_id=get_attr(d, 'powo', 'id'),
            iucn_id=get_attr(d, 'iucn', 'id'),
            iucn_category=get_attr(d, 'iucn', 'category'),
            common_names=combined_common_names,
        )
        species.write()
        return species

    @cached_property
    def full_name(self):
        return f'{self.name} ({self.genus.family.name})'

    @cache
    def get_common_names_str(self, delim=', ', max_len=None):
        if not max_len:
            return delim.join(self.common_names)

        common_names = []
        for common_name in self.common_names:
            if not common_name.isascii():
                continue
            if len(delim.join(common_names + [common_name])) > max_len:
                break
            common_names.append(common_name)
        return delim.join(common_names)
