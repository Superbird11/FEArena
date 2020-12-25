from django.db import models


class WeaponType(models.TextChoices):
    SWORD = 'Sword'
    LANCE = 'Lance'
    AXE = 'Axe'
    BOW = 'Bow'
    GAUNTLET = 'Gauntlet'
    HIDDEN = 'Hidden'
    TOME = 'Tome'
    FIRE = 'Fire'
    WIND = 'Wind'
    THUNDER = 'Thunder'
    LIGHT = 'Light'
    DARK = 'Dark'
    ANIMA = 'Anima'
    BLACK = 'Black Magic'
    WHITE = 'White Magic'
    STAFF = 'Staff'
    DRAGONSTONE = 'Dragonstone'
    BEAST = 'Beast Weapon'
    SPECIAL = 'Other'
