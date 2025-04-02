from aiogram.fsm.state import StatesGroup, State


class FilmSort(StatesGroup):
    search_query = State()


class FilmEdit(StatesGroup):
    edit_query = State()
    name = State()
    description = State()
    rating = State()
    genre = State()
    year = State()
    actors = State()
    poster = State()


class FilmDelete(StatesGroup):
    delete_query = State()


class FilmFilter(StatesGroup):
    filter_criteria = State()


class FilmForm(StatesGroup):
   name = State()
   description = State()
   rating = State()
   genre = State()
   year = State()
   actors = State()
   poster = State()

class SearchByActor(StatesGroup):
    actor_query = State()
