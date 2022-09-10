import uuid
from typing import Optional

class Serie:
    name: str = ""
    season: str = ""
    episode: str = ""
    def __init__(self, name, season, episode):
        self.name = name
        self.season = season
        self.episode = episode
