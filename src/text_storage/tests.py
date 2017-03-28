import datetime
import json
import itertools

from django.db.models import QuerySet
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.fields import DateTimeField
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .models import Text


class TextListAPIViewTestCase(TestCase):
    _ORDERING = ('-created_at', '-id')

    # ---- Utils ------------------------------------------------------------ #

    @classmethod
    def datetime_to_representation(cls, value: datetime.datetime) -> str:
        return DateTimeField().to_representation(value)

    @classmethod
    def create_random_texts(cls, page_count: int) -> None:
        Text.objects.bulk_create(
            Text(content=str(num))
            for num in range(api_settings.PAGE_SIZE * page_count)
        )

    @classmethod
    def build_texts_qs(cls, page_num: int) -> QuerySet:
        from_index = api_settings.PAGE_SIZE * (page_num - 1)
        to_index = api_settings.PAGE_SIZE * page_num
        return (
            Text.objects
            .order_by(*cls._ORDERING)
            [from_index:to_index]
        )

    def http_get_texts(self, **query_params) -> Response:
        return self.client.get(reverse('api.text_list'), data=query_params)

    def http_post_text(self, **text_data) -> Response:
        return self.client.post(
            reverse('api.text_list'),
            data=json.dumps(text_data),
            content_type='application/json',
        )

    # ---- Shortcuts -------------------------------------------------------- #

    def assertTextJsonEqualToText(self, text_json: dict, text: Text) -> None:
        self.assertDictEqual(
            text_json,
            {
                'id': text.id,
                'content': text.content,
                'created_at': self.datetime_to_representation(text.created_at),
            },
        )

    def assertTextsJsonEqualToPage(
        self, texts_json: list, page_num: int,
    ) -> None:
        texts = self.build_texts_qs(page_num=page_num).iterator()
        for text_json, text in itertools.zip_longest(texts_json, texts):
            self.assertTextJsonEqualToText(text_json, text)

    # ---- Testing ---------------------------------------------------------- #

    def test_text_json_representation(self):
        text = Text.objects.create(content='some_content')
        response = self.http_get_texts()
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_json['results']), 1)

        text_json = response_json['results'][0]
        self.assertTextJsonEqualToText(text_json, text)

    def test_get_texts_from_first_page(self):
        # Создаем объектов больше, чем помещается на одной странице
        first_page_num = 1
        self.create_random_texts(page_count=first_page_num + 1)

        response = self.http_get_texts()
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response_json['previous'])
        self.assertTrue(response_json['next'])
        self.assertTextsJsonEqualToPage(
            response_json['results'], first_page_num,
        )

    def test_get_texts_from_middle_page(self):
        # Создаем объектов больше, чем помещается на 2-х страницах
        # Это нужно, чтобы наполнить первую, среднюю и последную страницы
        # Берем не первую и не последнюю страницу
        middle_page_num = 2
        self.create_random_texts(page_count=middle_page_num + 1)

        response = self.http_get_texts(page=middle_page_num)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response_json['previous'])
        self.assertTrue(response_json['next'])
        self.assertTextsJsonEqualToPage(
            response_json['results'], middle_page_num,
        )

    def test_get_texts_from_last_page(self):
        # Создаем объектов больше, чем помещается на 2-х страницах
        # Это нужно, чтобы наполнить первую, среднюю и последную страницы
        # Берем не первую и не последнюю страницу
        last_page_num = 2
        self.create_random_texts(page_count=last_page_num)

        response = self.http_get_texts(page=last_page_num)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response_json['previous'])
        self.assertIsNone(response_json['next'])
        self.assertTextsJsonEqualToPage(
            response_json['results'], last_page_num,
        )

    def test_get_texts_from_nonexistent_page(self):
        first_page_num = 1
        last_page_num = 2
        self.create_random_texts(last_page_num)

        nonexistent_page_nums = (
            0,                      # - Не должно быть перевода на первую
                                    # страницу
            first_page_num - 1,     # - Перед первой
            last_page_num + 1,      # - После последней
            first_page_num - 1000,  # - Задолго до первой
            last_page_num + 1000,   # - Задолго после последней
        )
        for nonexistent_page_num in nonexistent_page_nums:
            with self.subTest(page_num=nonexistent_page_num):
                response = self.http_get_texts(page=nonexistent_page_num)
                response_json = response.json()
                self.assertEqual(
                    response.status_code, status.HTTP_404_NOT_FOUND,
                )
                self.assertDictEqual(
                    response_json, {'detail': 'Invalid page.'},
                )
    
    def test_create_text(self):
        self.assertListEqual(list(Text.objects.iterator()), [])

        text_content = 'some_content'
        response = self.http_post_text(content=text_content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        all_texts = list(Text.objects.iterator())
        self.assertEqual(len(all_texts), 1)

        text = all_texts[0]
        self.assertEqual(text.content, text_content)

        created_text_json = response.json()
        self.assertTextJsonEqualToText(created_text_json, text)

    def test_create_text_with_invalid_data(self):
        self.assertListEqual(list(Text.objects.iterator()), [])

        subtest_params_set = (
            {
                'request_data': {'content': ''},
                'response_data': {'content': ['This field may not be blank.']},
            },
            {
                'request_data': {'content': None},
                'response_data': {'content': ['This field may not be null.']},
            },
            {
                'request_data': {'nonexistent_field': 'some_value'},
                'response_data': {'content': ['This field is required.']},
            },
            {
                'request_data': {'nonexistent_field': None},
                'response_data': {'content': ['This field is required.']},
            },
            {
                'request_data': {},
                'response_data': {'content': ['This field is required.']},
            },
        )
        for subtest_params in subtest_params_set:
            with self.subTest(data=subtest_params):
                response = self.http_post_text(
                    **subtest_params['request_data'],
                )

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST,
                )
                self.assertDictEqual(
                    response.json(), subtest_params['response_data'],
                )
