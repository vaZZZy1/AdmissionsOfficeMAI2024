from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict
import json


@dataclass
class TextEntry:
    text: str


@dataclass
class RequestToML:
    entries: Dict[str, TextEntry] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({k: {"text": v.text} for k, v in self.entries.items()}, ensure_ascii=False, indent=2)


class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_data) -> RequestToML:
        """
        The method that should be implemented in the parser for websites,
        in the parser for tg chat, in the parser for excel tables.
        This method should receive data and convert it into a Request To ML structure.
        """


# # Example of using RequestToML structure:
#
# # Creating instance of RequestToML. It should be returned by all parsers for Mihail's ML job.
# data = {
#     "1": TextEntry(text="Расскажите, как правильно оценить свои шансы при пограничных (+-10) баллах?"),
#     "2": TextEntry(text="Сайты 11го не упадут?")
# }
# request_to_ml = RequestToML(entries=data)
# # RequestToML(entries={'1': TextEntry(text='Расскажите, как правильно оценить свои шансы при пограничных (+-10)
# # баллах?'), '2': TextEntry(text='Сайты 11го не упадут?')})
#
#
# # Jsonify structure. It may be useful.
# request_json = request_to_ml.to_json()
# # {
# #   "1": {
# #     "text": "Расскажите, как правильно оценить свои шансы при пограничных (+-10) баллах?"
# #   },
# #   "2": {
# #     "text": "Сайты 11го не упадут?"
# #   }
# # }
