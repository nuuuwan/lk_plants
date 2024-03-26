from functools import cache, cached_property

from utils import Log, Time, TimeFormat

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto

log = Log('InfoReadMe')


class InfoReadMe:
    MIN_CONFIDENCE = 0.2

    @staticmethod
    def is_in_geo(plant_photo):
        BOUNDS = [
            [6.911, 79.857],
            [6.917, 79.866],
        ]
        latlng = plant_photo.latlng

        return (
            BOUNDS[0][0] <= latlng.lat <= BOUNDS[0][1]
            and BOUNDS[1][0] <= latlng.lng <= BOUNDS[1][1]
        )
    
    @staticmethod
    def has_conf(plant_photo, conf=None):
        if not conf:
            conf = InfoReadMe.MIN_CONFIDENCE
        plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
        score = plant_net_result.top_score
        return score and score >= conf
    
    @staticmethod
    def should_analyze(plant_photo):
        return InfoReadMe.is_in_geo(plant_photo) and InfoReadMe.has_conf(plant_photo)
    
    @cached_property
    def data_list(self):
        data_list = PlantPhoto.list_all()
        data_vmd_park_list = [
            data for data in data_list if self.should_analyze(data)
        ]
        return data_vmd_park_list

    @cached_property
    def n_plant_photos(self):
        return len(self.data_list)

    @cached_property
    def time_str(self):
        return TimeFormat('%b %d, %Y (%I:%M %p)').stringify(Time.now())
    
    @cached_property
    def funnel(self) -> dict:
        raw =  [
            plant_photo for plant_photo in PlantPhoto.list_all_raw() 
        ]
        in_geo = [
            plant_photo for plant_photo in raw if self.is_in_geo(plant_photo)
        ]

        def get_conf( min_conf):
            return [
                plant_photo for plant_photo in in_geo if self.has_conf(plant_photo, min_conf)
            ]

        pct5_or_more = get_conf(0.05)
        pct10_or_more = get_conf(0.1) 
        pct20_or_more = get_conf(0.2)

        deduped = self.data_list

        return {
            "All":len(raw),
            "In Geo":len(in_geo),
            "≥ 5%":len(pct5_or_more),
            "≥ 10%": len(pct10_or_more),
            "≥ 20%": len(pct20_or_more),
            "Deduped": len(deduped),
        }