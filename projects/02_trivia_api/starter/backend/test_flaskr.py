import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        # new question data 
        self.new_question = {
            'question': 'Name a country in East Africa?',
            'answer': 'Kenya',
            'difficulty': 5,
            'category':1
        }

         # new wrong question data 
        self.new_wrong_question = {
            'answer': 'Kenya',
            'difficulty': 4,
            'category':1
        }


        # new question data 
        self.new_category = {
            'type': 'Mathematics',
           }

         # new wrong question data 
        self.new_wrong_category = {
            'question': 'Mathematics',
          
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_retrieve_questions(self):
        '''Test retrieve questions, check the status code, success, and if there is data available '''
        res= self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])

    def test_get_beyond_valid_page(self):
        '''Test for questions retrieval for pages beyond existing number of pages '''
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_create_new_question(self):
        '''Test for successfull creation of a new questions'''
        res = self.client().post('/questions',json = self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_create_new_questions_wrong_data(self):
        '''Test for creating a new question with wrong data '''
        res = self.client().post('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'server error')

    #    search test 

    def test_get_questions_search_with_results(self):
        '''
        Test to check for successfull searches
        '''
        res= self.client().post('/questions', json={'searchTerm':'The'})
        data = json.loads(res.data)
       
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])


    def test_get_questions_search_without_results(self):
        '''
        Test to check for  searches for a term not in the database 
        '''

        res = self.client().post('/questions', json={'searchTerm':'Maureen'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)

    def test_get_questions_for_a_category(self):
        #Test to get questions within a category 
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions'])) 
        self.assertTrue(data['total_questions'])  
        self.assertEqual(data['current_category'],'Science')


    def test_get_questions_for_a_nonexistent_category(self):
        #Test to get questions for a non-exisitent category
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'resource not found')



    def test_post_quiz_questions_allCategories(self):
        """" gets quiz questions with category = 0 """
        #request with previous questions as empty list
        res = self.client().post('/quizzes', json={'previous_questions':[] , 'quiz_category':{'id':0}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        #request with a previous question
        res = self.client().post('/quizzes', json={'previous_questions':[4] , 'quiz_category':{'id':1}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
      
    def test_post_quizzes_with_no_params(self):
        '''Test for post for quizzes with no params passed to the api'''
        res= self.client().post('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'server error')

    def test_delete_questions(self):
            '''Test for successful deletion of a question '''
            res = self.client().delete('/questions/2')
            data = json.loads(res.data)

            question = Question.query.filter(Question.id == 2).one_or_none()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(question, None)

    def test_delete_questions_fail(self):
            '''Test for failed deletion of a question '''
            res = self.client().delete('/questions/1000')
            data = json.loads(res.data)

           
            self.assertEqual(res.status_code, 422)
            self.assertEqual(data['success'], False)
            self.assertEqual(data['message'], 'unprocessable')

    
    def test_create_new_category(self):
        '''Test for successfull creation of a new category'''
        res = self.client().post('/categories',json = self.new_category)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_create_new_category_wrong_data(self):
        '''Test for creating a new category with wrong data '''
        res = self.client().post('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'server error')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()