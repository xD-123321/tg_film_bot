from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')
FILM_CREATE_COMMAND = Command("create_film")
SEARCH_MOVIE_COMMAND = Command('search_film')
FILTER_MOVIES_COMMAND = Command('filter_films')
EDIT_FILM_COMMAND = Command('edit_film')
DELETE_FILM_COMMAND = Command('delete_film')
SEARCH_FILM_BY_ACTOR = Command('search_by_actor')
FILM_STATS_COMMAND = Command('film_stats')

BOT_COMMANDS = [
    BotCommand(command='films', description="Перегляд списку фільмів"),
    BotCommand(command='start', description="Почати розмову"),
    BotCommand(command='create_film', description="Створити новий фiльм"),
    BotCommand(command='search_film', description="Пошук фiльму"),
    BotCommand(command='filter_films', description="Фiльтр фiльмiв"),
    BotCommand(command='edit_film', description="Редагування фiльму"),
    BotCommand(command='delete_film', description="Видалення фiльму"),
    BotCommand(command='search_by_actor', description="Пошук фiльму по актору"),
    BotCommand(command='film_stats', description="Статистика фільмів")]
