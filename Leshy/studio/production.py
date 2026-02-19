from enum import Enum, auto
from typing import List, Optional
from people import Director, Actor
from resources import Camera, MovieSet
from exceptions import NoneObjectError


class ProductionStatus(Enum):
    PLANNED = auto()
    SCRIPT_READY = auto()
    CASTING_DONE = auto()
    FILMED = auto()
    POST_PROD_DONE = auto()
    RELEASED = auto()


class Script:
    def __init__(self, title: str, genre: str, pages: int):
        self._title = title
        self._genre = genre
        self._pages = pages

    @property
    def title(self) -> str: return self._title

    @property
    def genre(self) -> str: return self._genre

    @property
    def pages(self) -> int: return self._pages


class Movie:
    def __init__(self, script: Script):
        if not isinstance(script, Script):
            raise NoneObjectError("Movie must be initialized with a Script object.")
        self._script = script
        self._status = ProductionStatus.PLANNED
        self._director: Optional[Director] = None
        self._cast: List[Actor] = []
        self._camera: Optional[Camera] = None
        self._movie_set: Optional[MovieSet] = None
        self._final_cut: Optional[str] = None

    @property
    def script(self) -> Script: return self._script

    @property
    def status(self) -> ProductionStatus: return self._status

    @status.setter
    def status(self, value: ProductionStatus): self._status = value

    @property
    def director(self) -> Optional[Director]: return self._director

    @director.setter
    def director(self, value: Director): self._director = value

    @property
    def cast(self) -> List[Actor]: return self._cast

    def add_actor(self, actor: Actor): self._cast.append(actor)

    @property
    def camera(self) -> Optional[Camera]: return self._camera

    @camera.setter
    def camera(self, value: Camera): self._camera = value

    @property
    def movie_set(self) -> Optional[MovieSet]: return self._movie_set

    @movie_set.setter
    def movie_set(self, value: MovieSet): self._movie_set = value

    @property
    def final_cut(self) -> Optional[str]: return self._final_cut

    @final_cut.setter
    def final_cut(self, value: str): self._final_cut = value

    def __str__(self) -> str:
        director_name = self._director.name if self._director else "None"
        cast_count = len(self._cast)
        return (f"Movie: '{self._script.title}' | Genre: {self._script.genre} | "
                f"Status: {self._status.name} | Director: {director_name} | "
                f"Cast: {cast_count} actors")