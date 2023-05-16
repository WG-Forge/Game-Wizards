import os
import random

import pygame_menu
from pygame_menu import Theme, BaseImage

from src.constants import BLACK


def get_random_picture_path(folder_path: str = 'src/assets/background_images') -> str | None:
    picture_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    picture_files = [f for f in os.listdir(folder_path) if
                     os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[
                         1].lower() in picture_extensions]
    if picture_files:
        return os.path.join(folder_path, random.choice(picture_files))
    else:
        return None


def random_background() -> BaseImage:
    image = pygame_menu.BaseImage(get_random_picture_path())
    image.set_alpha(180)
    return image


def load_default_theme() -> Theme:
    main_theme = Theme()
    main_theme.background_color = random_background()
    main_theme.title = False
    main_theme.widget_font = "src/assets/screen/BF_Modernista-Regular.ttf"
    main_theme.widget_font_size = 18
    main_theme.widget_font_color = BLACK
    main_theme.widget_background_color = (205, 205, 205, 128)
    main_theme.widget_border_width = 5
    main_theme.widget_border_color = (50, 50, 50)
    main_theme.widget_margin = (0, 0)
    main_theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
    main_theme.border_color = (150, 150, 150)
    main_theme.selection_color = (0, 0, 128)
    main_theme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection()
    return main_theme
