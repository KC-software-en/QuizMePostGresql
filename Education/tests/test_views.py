# import the required libraries
# import ast safely evaluate strings containing Python literal structures e.g.strings, lists, dicts
# use to convert str into list
### Run commands for test ###
# coverage erase
# python manage.py test Education.tests.test_views
# coverage run --source='.' manage.py test Education
# coverage report
# coverage html

import requests
import ast 
import sys
import unittest
from django.contrib.messages.middleware import MessageMiddleware
from django.template.response import SimpleTemplateResponse
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.hashers import make_password
from unittest.mock import patch, MagicMock, Mock
from django.test.client import RequestFactory, Client
from django.http import HttpResponse, HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# import functions from utils.py called in views
from ..utils import (
    get_json_categories,
    get_category_names,
    get_specific_json_category,
    mix_choices,
)

from ..models import *

# import the views to be tested
from Education.views import *
from user_auth.views import *

'''
# create a test case for the views
# tests for index view
class TestIndexView(TestCase):
    # create a setUp method to create a user and login before each test
    def setUp(self):
        # Create a request factory
        self.factory = RequestFactory()

    def test_session_key_exists(self):
        # Create a request with 'quiz_result' in session
        request = self.factory.get('/')
        request.session = {'quiz_result': 'some_value'}

        # Call the index view
        response = index(request)

        # Check if 'quiz_result' is removed from session
        self.assertNotIn('quiz_result', request.session)
        self.assertIsInstance(response, HttpResponse)

    def test_session_key_not_exists(self):
        # Create a request without 'quiz_result' in session
        request = self.factory.get('/')
        request.session = {}

        # Call the index view
        response = index(request)

        # Check if 'quiz_result' is not removed from session
        self.assertNotIn('quiz_result', request.session)
        self.assertIsInstance(response, HttpResponse)

# Test for Index_edu view
class TestIndexEduView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('Education.views.get_json_categories')
    @patch('Education.views.get_category_names')
    @patch('Education.views.category_objects')
    def test_index_edu(self, mock_category_objects, mock_get_category_names, mock_get_json_categories):
        mock_get_json_categories.return_value = 'mocked_categories'
        mock_get_category_names.return_value = ['mocked_category_name']
        mock_category_objects.return_value = 'mocked_question_selection'

        request = self.factory.get('/Education/')
        request.session = {'quiz_result': 'some_result', 'question_selection_ids': [1, 2, 3]}

        response = index_edu(request)
        
        self.assertEqual(response.status_code, 200)
        mock_get_json_categories.assert_called_once()
        mock_get_category_names.assert_called_once_with('mocked_categories')
        mock_category_objects.assert_called_once_with(request, 'mocked_category_name')

# Test for the Detail view  
class TestDetailView(TestCase):    
    def setUp(self):
        self.client = Client()

    def test_detail_view_with_valid_question(self):
        # Create a mock request with category_name and question_id
        request = self.client.get('/Education/category/1')
        request.user = Mock()

        # Mock the necessary functions
        get_json_categories = Mock(return_value={'categories': [{'name': 'category1'}, {'name': 'category2'}]})
        get_category_names = Mock(return_value=['category1', 'category2'])
        find_model = Mock(return_value=Mock())
        get_object_or_404 = Mock(return_value=Mock(
            pk=1,
            correct_answer='Answer',
            choices='["Choice 1", "Choice 2", "Choice 3"]'
        ))

        # Patch the necessary functions
        with patch('Education.views.get_json_categories', get_json_categories), \
             patch('Education.views.get_category_names', get_category_names), \
             patch('Education.views.find_model', find_model), \
             patch('Education.views.get_object_or_404', get_object_or_404):
            response = detail(request, 'category1', 1)
        
        # Assert that the correct template is rendered
        self.assertEqual(response, 'edu_quiz/edu_detail.html')

        # Assert that the context contains the expected values
        self.assertEqual(response.context_data['question'].pk, 1)
        self.assertEqual(response.context_data['question'].correct_answer, 'Answer')
        self.assertEqual(response.context_data['choices'], ['Choice 1', 'Choice 2', 'Choice 3'])
        self.assertEqual(response.context_data['category_name'], 'category1')

    def test_detail_view_with_invalid_question(self):
        # Create a mock request with category_name and question_id
        request = self.client.get('<str:category_name>/<int:question_id>/detail/')
        request.user = Mock()

        # Mock the necessary functions
        get_json_categories = Mock(return_value={'trivia_categories"': [{'name': 'category1'}, {'name': 'category2'}]})
        get_category_names = Mock(return_value=['category1', 'category2'])
        find_model = Mock(return_value=Mock())
        get_object_or_404 = Mock(side_effect=Http404)

        # Patch the necessary functions
        with patch('Education.views.get_json_categories', get_json_categories), \
             patch('Education.views.get_category_names', get_category_names), \
             patch('Education.views.find_model', find_model):
                response = detail(request, 'category1', 2)             

        # Assert that the correct template is rendered
        self.assertEqual(response.template_name, 'edu_quiz/edu_detail.html')

        # Assert that the context contains the expected values
        self.assertIsNone(response.context_data['question'])
        self.assertEqual(response.context_data['choices'], [])
        self.assertEqual(response.context_data['category_name'], 'category1')

    

# Test for the results view
class ResultsViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_results_view_requires_login(self):
        # Create a request object
        request = HttpRequest()
        request.user = self.user
        req = self.client.get(reverse('Education:results', args=['History']))
        middleware = SessionMiddleware(get_response=req)
        middleware.process_request(request)
        request.session.save()

        category_name = 'History'

        # Call the view function
        response = results(request, category_name)

        self.assertEqual(response.status_code, 200)

    def test_results_view_with_authenticated_user(self):
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Replace 'your_category_name' with the actual category name
        category_name = 'History'

        # Call the view function
        response = self.client.get(reverse('Education:results', args=[category_name]))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # You can add more assertions here based on your view's behavior

        # Example: Check if the correct template is used
        self.assertTemplateUsed(response, 'edu_quiz/edu_result.html')

        # Example: Check if the 'result' and 'category_name' are in the context
        self.assertIn('result', response.context)
        self.assertEqual(response.context['category_name'], category_name)
        '''
# Test for the selection views
class SelectionTestCase(TestCase): 
    def setup(self):
        self.factory = RequestFactory()      
    @patch('Education.views.ast') 
    def test_selection_valid_category_and_question(self, mock_ast):
        # Mock functions
        get_json_categories = MagicMock(return_value={"Mythology": {}, "History": {}})
        get_category_names = MagicMock(return_value=["Mythology", "History"])
        get_object_or_404 = MagicMock()
        model = MagicMock()
        model.objects.get = MagicMock()

        # Set request object with valid choice
        request = MagicMock()
        request.POST = {'choice': 1}
        mock_convert_choices = ['choice1', 'choice2']
        mock_ast.literal_eval.return_value = mock_convert_choices
        mock_question = MagicMock()

        # Call function
        response = selection(request, 'History', 1)

        # Assertions
        # Assert that the correct template is rendered
        self.assertEqual(response, 'edu_quiz/edu_detail.html')
        self.assertTemplateUsed,(response, 'edu_quiz/edu_detail.html')
        ast.literal_eval.assert_called_once_with(get_object_or_404.return_value.choices)
        model.objects.get.assert_called_once_with(pk=request.POST['choice'])
        assert get_json_categories() == {"Mythology": {}, "History": {}}, "get_json_categories did not return the expected value"
        assert get_category_names() == ["Mythology", "History"], "get_category_names did not return the expected value"
        mock_ast.literal_eval.assert_called_once_with(mock_question.choices)

    def test_selection_view_with_no_model(self):
        request = MagicMock()
        self.client = Client()
        request.user = Mock()

        # Mock the necessary functions
        
        find_model = Mock(return_value=Mock())
        get_object_or_404 = Mock(return_value=Mock(
            pk=1,
            correct_answer='Choice 1',
            choices='["Choice 1", "Choice 2", "Choice 3"]'
        ))

        # Patch the necessary functions
        with patch('Education.views.get_json_categories', get_json_categories), \
             patch('Education.views.get_category_names', get_category_names), \
             patch('Education.views.find_model', find_model), \
             patch('Education.views.get_object_or_404', get_object_or_404):
            response = selection(request, 'category1', 2)

        # Assert that get_object_or_404 was called
        get_object_or_404.assert_called_once()    
        get_object_or_404.assert_called_with('category1', 1)
        
        # Assert that the correct template is rendered
        self.assertEqual(response, 'edu_quiz/edu_detail.html')
        self.assertTemplateUsed,(response, 'edu_quiz/edu_detail.html')

        # Assert that the error message is present in the response
        self.assertIn("You didn't select a choice.", response['error_message'])


        # Assert that the context contains the expected values
        self.assertEqual(response.context_data['question'].pk, 1)
        self.assertEqual(response.context_data['question'].correct_answer, 'Choice 1')
        self.assertEqual(response.context_data['choices'], ['Choice 1', 'Choice 2', 'Choice 3'])
        self.assertEqual(response.context_data['category_name'], 'category1')      
      

'''
# Test for the try new quiz view  
class TestTryNewQuiz(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_try_new_quiz_with_quiz_result_in_session(self):
        # Create a session with 'quiz_result'
        session = {'quiz_result': 5}
        request = self.factory.get(try_new_quiz)
        request.session = session

        # Call the view function
        response = try_new_quiz(request)

        # Assertions
        self.assertNotIn('quiz_result', request.session)  # Assert session data has been deleted
        self.assertIsInstance(response, HttpResponseRedirect)  # Assert response is a redirect
        self.assertEqual(response.url, reverse('Education:index_edu'))  # Assert redirect URL is correct

# Test for the try new quiz view  with results
    @patch('django.shortcuts.reverse')  # Patch reverse function
    def test_try_new_quiz_with_result(self, mock_reverse):
        # Mock reverse function
        mock_reverse.return_value = '/Education/try_new_quiz/'  # Replace with the expected redirect URL

        # Create a mock request object with "quiz_result" in the session
        request = MagicMock()
        request.session = {'quiz_result': 5}

        # Call the function
        response = try_new_quiz(request)

        # Assert expected behavior
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/Education/')

        # Assert "quiz_result" is deleted
        self.assertNotIn('quiz_result', request.session) 

    def test_try_new_quiz_without_quiz_result_in_session(self):
        # Create a session without 'quiz_result'
        request = RequestFactory().get(try_new_quiz)
        # Add middleware manualy
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()

        # Call the view function
        response = try_new_quiz(request)

        # Assertions
        self.assertNotIn('quiz_result', request.session)  # Assert session data has not been modified
        self.assertIsInstance(response, HttpResponseRedirect)  # Assert response is a redirect
        self.assertEqual(response.url, reverse('Education:index_edu'))  # Assert redirect URL is correct 
'''