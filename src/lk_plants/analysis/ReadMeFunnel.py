import os
from functools import cached_property

import matplotlib.pyplot as plt
from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeFunnel')


class ReadMeFunnel(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.funnel.md'

    def build_chart(self):
        plt.close()
        funnel = self.funnel
        x = list(funnel.keys())[::-1]
        y = list(funnel.values())[::-1]
        color = ['#ccc', '#888', '#c00', '#f80', '#0808', '#080'][::-1]
        bars = plt.barh(x, y, color=color)

        plt.grid(False)
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        plt.title('Plant Photo Funnel')
        for bar, value in zip(bars, y):
            plt.text(bar.get_width() + 10, bar.get_y() + 0.3, str(value))

        chart_path = os.path.join('images', 'funnel.png')
        plt.savefig(chart_path)
        plt.close()
        log.info(f'Wrote {chart_path_unix}')

        return Markdown.image('funnel', chart_path_unix)

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Plant Photo Funnel',
            '',
            self.build_chart(),
        ]
