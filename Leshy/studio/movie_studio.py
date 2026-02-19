from typing import List
from people import Director, Actor
from resources import Camera, MovieSet, Montage, PostProduction
from production import Movie, Script, ProductionStatus
from exceptions import (
    ResourceBusyError, WorkflowOrderError,
    NoneObjectError, GenreMismatchError
)


class MovieStudio:
    def __init__(self, name: str):
        self._name = name
        self._movies: List[Movie] = []
        self._directors: List[Director] = []
        self._actors: List[Actor] = []
        self._cameras: List[Camera] = []
        self._sets: List[MovieSet] = []
        self._montage_dept = Montage("Adobe Premiere")
        self._post_prod_dept = PostProduction("ILM")

    @property
    def movies(self) -> List[Movie]:
        return self._movies

    @property
    def directors(self) -> List[Director]:
        return self._directors

    def hire_director(self, name: str, style: str):
        self._directors.append(Director(name, style))

    def hire_actor(self, name: str, rank: str):
        self._actors.append(Actor(name, rank))

    def buy_camera(self, model: str, resolution: str):
        self._cameras.append(Camera(model, resolution))

    def build_set(self, location: str, is_indoor: bool):
        self._sets.append(MovieSet(location, is_indoor))

    def create_script(self, title: str, genre: str, pages: int) -> int:
        script = Script(title, genre, pages)
        new_movie = Movie(script)
        new_movie.status = ProductionStatus.SCRIPT_READY
        self._movies.append(new_movie)
        return len(self._movies) - 1

    def perform_casting(self, movie_idx: int, director_idx: int, actor_indices: List[int]):
        movie = self._get_movie_safe(movie_idx)

        if not (0 <= director_idx < len(self._directors)):
            raise NoneObjectError(f"Director ID {director_idx} not found.")

        director = self._directors[director_idx]

        if director.style.lower() != movie.script.genre.lower():
            raise GenreMismatchError(
                f"Director style '{director.style}' does not match genre '{movie.script.genre}'"
            )

        if director.is_busy:
            raise ResourceBusyError(f"Director {director.name} is busy.")

        candidates = []
        for a_idx in actor_indices:
            if not (0 <= a_idx < len(self._actors)):
                raise NoneObjectError(f"Actor ID {a_idx} not found.")
            actor = self._actors[a_idx]
            if actor.is_busy:
                raise ResourceBusyError(f"Actor {actor.name} is busy.")
            candidates.append(actor)

        movie.director = director
        director.is_busy = True

        for actor in candidates:
            movie.add_actor(actor)
            actor.is_busy = True

        movie.status = ProductionStatus.CASTING_DONE

    def start_filming(self, movie_idx: int, camera_idx: int, set_idx: int):
        movie = self._get_movie_safe(movie_idx)
        if movie.status != ProductionStatus.CASTING_DONE:
            raise WorkflowOrderError("Casting must be done before filming.")

        if not (0 <= camera_idx < len(self._cameras)):
            raise NoneObjectError("Camera not found.")
        camera = self._cameras[camera_idx]
        if camera.is_busy:
            raise ResourceBusyError(f"Camera {camera.model} is busy.")

        if not (0 <= set_idx < len(self._sets)):
            raise NoneObjectError("Movie Set not found.")
        movie_set = self._sets[set_idx]
        if movie_set.is_busy:
            raise ResourceBusyError(f"Set {movie_set.location} is busy.")

        movie.camera = camera
        camera.is_busy = True

        movie.movie_set = movie_set
        movie_set.is_busy = True

        movie.status = ProductionStatus.FILMED

    def run_post_production(self, movie_idx: int):
        movie = self._get_movie_safe(movie_idx)
        if movie.status != ProductionStatus.FILMED:
            raise WorkflowOrderError("Filming must be finished first.")

        edit_log = self._montage_dept.apply_edits(movie.script.title)
        vfx_log = self._post_prod_dept.finalize_movie(movie.script.title)
        movie.final_cut = f"{edit_log} | {vfx_log}"
        movie.status = ProductionStatus.POST_PROD_DONE

    def release_movie(self, movie_idx: int):
        movie = self._get_movie_safe(movie_idx)
        if movie.status != ProductionStatus.POST_PROD_DONE:
            raise WorkflowOrderError("Post-production not finished.")

        if movie.director:
            movie.director.is_busy = False

        for actor in movie.cast:
            actor.is_busy = False

        if movie.camera:
            movie.camera.is_busy = False

        if movie.movie_set:
            movie.movie_set.is_busy = False

        movie.status = ProductionStatus.RELEASED

    def _get_movie_safe(self, idx: int) -> Movie:
        if 0 <= idx < len(self._movies):
            return self._movies[idx]
        raise NoneObjectError(f"Movie ID {idx} is out of range.")