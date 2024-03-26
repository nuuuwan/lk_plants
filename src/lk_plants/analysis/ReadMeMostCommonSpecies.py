from functools import cached_property

from utils import Log

from lk_plants.analysis.ReadMeStatisticsByTaxonomy import \
    ReadMeStatisticsByTaxonomy
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.taxonomy.Species import Species
from lk_plants.core.wiki.WikiPage import WikiPage
from utils_future import Markdown

log = Log('ReadMeMostCommonSpecies')


class ReadMeMostCommonSpecies(ReadMeStatisticsByTaxonomy):
    @staticmethod
    def get_lines_for_species(species_name, plant_photo_list):
        MAX_PLANT_PHOTOS = 3
        plant_photo_list.sort(
            key=lambda x: list(
                PlantNetResult.from_plant_photo(
                    x
                ).species_name_to_score.items()
            )[0][1],
            reverse=True,
        )
        best_plant_photos = plant_photo_list[:MAX_PLANT_PHOTOS]

        image_md_list = []
        for plant_photo in best_plant_photos:
            image_path = plant_photo.image_path
            image_path_unix = image_path.replace('\\', '/')
            p_width = 1.0/MAX_PLANT_PHOTOS - 0.1
            width = f'{p_width:.0%}'
            image_md = Markdown.image_html(
                species_name, image_path_unix, width
            )
            image_md_list.append(image_md)
        image_all_md = ' '.join(image_md_list)

        plant_net_result = PlantNetResult.from_plant_photo(
            best_plant_photos[0]
        )
        species_name = plant_net_result.top_species_name
        species = Species.from_name(species_name)
        wiki_page_name = species.wiki_page_name
        wiki_page = WikiPage.from_wiki_page_name(wiki_page_name)
        summary = wiki_page.summary

        n_photos = len(plant_photo_list)

        lines = [
            f'### *{species_name}*',
            '',
            f'*{n_photos} Photos*',
            '',
            image_all_md,
            '',
            summary +  ' ' + Markdown.ref(Markdown.wiki_link(wiki_page_name, 'Wikipedia')),
            '',
        ]
        return lines

    @cached_property
    def lines_most_common_species(self):
        key_and_data_list = self.get_sorted_key_and_data_list(
            ReadMeStatisticsByTaxonomy.get_key_species
        )
        lines = []
        for key, data_list in key_and_data_list[
            : ReadMeStatisticsByTaxonomy.N_DISPLAY
        ]:
            lines.extend(
                ReadMeMostCommonSpecies.get_lines_for_species(key, data_list)
            )
        return lines

    @cached_property
    def file_path(self):
        return 'README.statistics.taxonomy.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Most Common Species',
            '',
        ] + self.lines_most_common_species