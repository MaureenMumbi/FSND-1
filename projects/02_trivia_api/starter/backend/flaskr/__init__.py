import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask_migrate import Migrate

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app,
                resources={r"/*": {"origins": "*"}},
                supports_credentials=True)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,PUT,DELETE,OPTIONS')
        return response


#  to fetch categories which are returned in the questions endpoint


    def get_category_list():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        return categories

# GET requests for questions, the endpoint includes pagination (every 10 questions).
# This endpoint returns a list of questions, number of total questions,
# current category, categories.
    @app.route('/questions')
    def getquestions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': get_category_list(),
            'total_questions': len(Question.query.all()),
            'current_category': None
        })

    # Used to DELETE question using a question ID.
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True
            })

        except BaseException:
            abort(422)
   
    # POST a new question,  which will require the question and answer text,
    # category, and difficulty score. If a search term is provided this endpoint will return the search results

    @app.route('/questions', methods=['POST'])
    def add_question():
        question = request.get_json()
        new_question = question.get('question', None)
        new_answer = question.get('answer', None)
        new_difficulty = question.get('difficulty', None)
        new_category = question.get('category', None)
        new_rating = question.get('rating', None)
        search_term = question.get('searchTerm', None)
        try:

            if search_term:
                results = Question.query.order_by(
                    Question.id).filter(
                    Question.question.ilike(
                        '%{}%'.format(search_term)))

                current_questions = paginate_questions(request, results)
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(results.all())
                })

            else:
                questions = Question(question=new_question,
                                     answer=new_answer,
                                     difficulty=new_difficulty,
                                     category=new_category,
                                     rating=new_rating)
                questions.insert()

                allquestions = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, allquestions)

                return jsonify({
                    'success': True,
                    'created': questions.id,
                    'questions': current_questions,
                    'total_questions': len(allquestions)

                })
        except BaseException:
            abort(422)

# Gets the category name using the id
    def getCategory(id):
        category = Category.query.filter(Category.id == id).one_or_none()

        if category is None:
            abort(404)

        return category.format()["type"]

# GET endpoint to get questions based on category
    @app.route('/categories/<int:category>/questions')
    def get_questions_by_category(category):
        questions = Question.query.filter(
            Question.category == category).order_by(
            Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': getCategory(category)
        })

# POST endpoint to get questions to play the quiz.
# This endpoint takes category and previous question parameters  and
# return a random questions within the given category, if provided, and
# that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        previous_questions = body.get('previous_questions',None)
        quiz_category = body.get('quiz_category', None)
        print(len(previous_questions))
        print(previous_questions)

        try:

            if int(quiz_category.get('id')) == 0 & len(
                    previous_questions) == 0:
                questions = Question.query.all()
            elif int(quiz_category.get('id')) != 0:
                questions = Question.query.filter(
                    Question.category == quiz_category.get('id')).all()
            if not questions:
                return abort(422)
            selected = []
            for question in questions:
                if question.id not in previous_questions:
                    selected.append(question.format())
            if len(selected) != 0:
                result = random.choice(selected)
                return jsonify({
                    'success': True,
                    'question': result
                })
            else:
                return jsonify({
                    'success': False,

                })
        except Exception:
            abort(422)

# POST a new category,  which will require the category type
    @app.route('/categories', methods=['POST'])
    def add_category():
        data = request.get_json()
        new_type = data.get('type', None)

        try:
            category = Category(type=new_type)
            category.insert()

            allcategories = Category.query.order_by(Category.id).all()
            categorylist = [category.format() for category in allcategories]

            return jsonify({
                'success': True,
                'created': category.id,
                'categories': categorylist,
                'total_categories': len(allcategories)

            })
        except BaseException:
            abort(422)

# Used to paginate questions into 10 questions per page 
    def paginate_questions(request, data):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in data]
        current_questions = questions[start:end]

        return current_questions


# Error handlers for 400, 404, 422 and 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'server error'
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    return app
