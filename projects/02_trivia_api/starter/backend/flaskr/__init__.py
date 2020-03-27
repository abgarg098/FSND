import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  current_questions= questions[start:end]

  return current_questions

class AbortError(Exception):
  def __init__(self, code):  
        self.code = code  
  
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origins', '*')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  
  @app.route('/categories')
  def retrieve_categories():
    categories = {category.id:category.type for category in Category.query.all()}
   
    
    if len(categories) == 0:
      abort(404)

    obj = jsonify({
      'success': True,
      'categories': categories
    })
    return obj

  
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = {category.id:category.type for category in Category.query.all()}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      "categories": categories,
      "current_category": None,
    })



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        raise AbortError(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id,
        'total_questions': len(Question.query.all())
      })

    except AbortError as e:
      abort(e.code)
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    if body == None:
      abort(422)

    search_term = body.get('searchTerm')
    
    try:
      if search_term:
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0: 
          raise AbortError(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(selection.all()),
          'current_category': None
        })

      else:
        new_title = body.get('question', None)
        if new_title == None:
          raise AbortError(404)
        new_answer = body.get('answer', None)
        if new_answer == None:
          raise AbortError(404)
        new_difficulty= body.get('difficulty', None)
        if new_difficulty == None:
          raise AbortError(404)
        new_category= body.get('category', None)
        if new_category == None:
          raise AbortError(404)

        
        question = Question(new_title, new_answer, new_category, new_difficulty)
        question.insert()

        return jsonify({
          'success': True,
          'created': question.id,
          'total_questions': len(Question.query.all())
        })

    except AbortError as e:
      abort(e.code)
    except:
      abort(422)
  

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start.

  '''

  #  Done 

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def retrieve_categories_by_id(category_id):
    
    category = Category.query.get(category_id)
    selection = Question.query.order_by(Question.id).filter_by(category=category_id)
    current_questions = paginate_questions(request, selection)
    
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection.all()),
      'current_category': category.format()
    })
    
    

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()

    try:
      previous_questions = body.get('previous_questions', None)
      quiz_category =  body.get('quiz_category', None)
      quiz_category_id = quiz_category.get('id', -1)

      if quiz_category_id == 0:
          selection = Question.query.order_by(Question.id).filter(Question.id.notin_(previous_questions)).all()
      
      else:
        category = Category.query.get(quiz_category_id)
        if category == None:
          raise AbortError(404)
        selection = Question.query.order_by(Question.id).filter_by(category=quiz_category_id).filter(Question.id.notin_(previous_questions)).all()
      
      selection_length = len(selection)
      
      if selection_length > 0:
        selected_question = selection[random.randrange(0, selection_length)]
        return jsonify({
          'success': True,
          "question": selected_question.format()
        })
      else:
        return jsonify({
                  "success": True,
                  "question": None
                })

    except AbortError as e:
      abort(e.code)
    except:
      abort(422)
  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  return app

    