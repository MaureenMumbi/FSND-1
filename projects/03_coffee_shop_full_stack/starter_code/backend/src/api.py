import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()



# ROUTES
'''
Get Drinks without requiring a token 
    GET /drinks endpoint which
        - should be a public endpoint
        - should contain only the drink.short() data representation
        - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    
    if not drinks:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

'''
Get Drink Details
       GET /drinks-detail endpoint
        - should require the 'get:drinks-detail' permission
        - should contain the drink.long() data representation
        - returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getdrinkdetails(payload):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)
    
    drinkdetails =[drink.long() for drink in drinks]
    return jsonify({
        'success':True,
        'drinks':drinkdetails
    })

'''
Create a new drink
    POST /drinks endpoint
        - should create a new row in the drinks table
        - should require the 'post:drinks' permission
        - should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createdrink(payload):
    data = request.get_json()
    print(data)
    print(payload)

    try:
        new_title = data.get('title', None)
        new_recipes = json.dumps(data.get('recipe', None))
        drink = Drink(title=new_title, recipe=new_recipes)
        drink.insert()
    except Exception as e:
        print(e)
        abort(404)
    
    return jsonify({
        'success':True,
        'drinks': [drink.long()]
    })


'''
Update Drinks
    PATCH /drinks/<id> endpount
        where <id> is the existing model id
        - should respond with a 404 error if <id> is not found
        - should update the corresponding row for <id>
        - should require the 'patch:drinks' permission
        - should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updatedrink(payload, id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == id ).one_or_none()

    if not drink:
        abort(404)
    
    try: 
     updated_title= data.get('title', None)
     updated_recipe = json.dumps(data.get('recipe', None))

     if updated_title:
         drink.title =updated_title
     if updated_recipe:
         drink.recipe= updated_recipe
    
     drink.update()
    
    except BaseException:
        abort(400)
    
    return jsonify({
        'success':True,
        'drinks': [drink.long()]
    }),200

'''
Delete Drink
    DELETE /drinks/<id> endpoint
        where <id> is the existing model id
        - should respond with a 404 error if <id> is not found
        - should delete the corresponding row for <id>
        - should require the 'delete:drinks' permission
        - returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
        
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deletedrinks(payload, id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()

    if not drink:
        abort(404)
    try:
        drink.delete()
    except BaseException:
        abort(400)

    return jsonify({
        'success': True,
        'delete':id
    }),200
    

# Error Handling
'''
    error handler for 422
  
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
    error handler for 400
  
'''
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

'''
    error handler for 500
  
'''
@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

'''
    error handler for 405
  
'''

@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


'''
    error handler for 404
   
'''

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404


'''
    error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
