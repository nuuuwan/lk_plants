import os
from datetime import datetime
from functools import cached_property

import matplotlib.pyplot as plt
from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.analysis.readme_pages.ReadMeFunnel import ReadMeFunnel
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeFunnelByDay')


class ReadMeFunnelByDay(MarkdownPage, InfoReadMe):
    MIN_DAYS_DISPLAY = 14

    @cached_property
    def file_path(self):
        return 'README.funnel_by_day.md'

    def get_data(self):
        funnel_idx = self.get_funnel(func_get_key=lambda x: x.date_str)
        key_and_stats = list(funnel_idx.items())[
            -ReadMeFunnelByDay.MIN_DAYS_DISPLAY:
        ]

        x = [datetime.strptime(item[0], '%Y-%m-%d') for item in key_and_stats]

        ys = {}
        for item in key_and_stats:
            for k, v in item[1].items():
                if k not in ys:
                    ys[k] = []
                ys[k].append(v)
        return x, ys

    @cached_property
    def lines_chart(self) -> list[str]:
        plt.close()

        x, ys = self.get_data()

        plt.figure(figsize=(16, 9))
        plt.tight_layout(pad=2.0)

        plt.xticks(rotation='vertical')

        for i, [k, y] in enumerate(ys.items()):
            plt.bar(x, y, label=k, color=ReadMeFunnel.FUNNEL_COLORS[i])

        plt.legend()
        plt.title(
            'Duplicates by Date '
            + f'(Last {ReadMeFunnelByDay.MIN_DAYS_DISPLAY})'
        )

        chart_path = os.path.join('images', 'duplicates_by_date.png')
        plt.savefig(chart_path)
        plt.close()

        log.info(f'Wrote {chart_path}')
        os.startfile(chart_path)

        chart_path_unix = chart_path.replace('\\', '/')
        return Markdown.image('Duplicates by Date', chart_path_unix)

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Funnel by Day',
            '',
            self.lines_chart,
            '',
        ]
