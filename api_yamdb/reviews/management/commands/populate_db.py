#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 22:33:13 2024

@author: alexandermikhailov
"""


import csv
from enum import Enum
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand
from django.db.models.base import ModelBase
from reviews.models import Category, Comment, Genre, Review, Title, User

DB_NAME = 'db.sqlite3'
PATH_DATA = 'static/data'
PATH = Path(__file__).resolve().parent.parent.parent.parent.joinpath(PATH_DATA)


class ModelFileMatch(str, Enum):

    def __new__(
        cls, value: str, model: ModelBase, fieldnames: Optional[tuple]
    ):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.model = model
        obj.fieldnames = fieldnames
        return obj

    CATEGORY = 'category.csv', Category, None
    GENRE = 'genre.csv', Genre, None
    TITLE = 'titles.csv', Title, ('id', 'name', 'year', 'category_id')
    USER = 'users.csv', User, None
    COMMENT = 'comments.csv', Comment, (
        'id', 'review_id', 'text', 'author_id', 'pub_date'
    )
    # NONE = 'genre_title.csv', None, None
    REVIEW = 'review.csv', Review, (
        'id', 'title_id', 'text', 'author_id', 'score', 'pub_date'
    )


class Command(BaseCommand):

    help = f'''Populates {DB_NAME} Database with the Data from csv-Files
Located within {PATH_DATA}'''

    def handle(self, *args, **options) -> None:

        for match in ModelFileMatch:
            if match.model.objects.exists():
                continue
            with open(
                Path(PATH).joinpath(match.value), encoding='utf8'
            ) as file:
                reader = csv.DictReader(file, fieldnames=match.fieldnames)
                if match.fieldnames:
                    next(reader)
                match.model.objects.bulk_create(
                    match.model(**_) for _ in reader
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'''Successfully Populated {DB_NAME} Database with the
Data from csv-Files Located within {PATH_DATA}'''
            )
        )
