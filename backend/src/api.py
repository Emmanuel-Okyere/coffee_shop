"""Flask Application"""
import json

from flask import Flask, abort, jsonify, request
from flask_cors import CORS

from .auth.auth import AuthError, requires_auth
from .database.models import Drink, db_drop_and_create_all, setup_db

app = Flask(__name__)
setup_db(app)
CORS(app)


# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# !! Running this funciton will add one

# db_drop_and_create_all()

# ROUTES

@app.route('/drinks',methods=['GET'])
def get_drinks():
    '''
    @TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.all()
    formatted_drink = [drink.short() for drink in drinks]
    return jsonify({
        'success':True,
        'drinks': formatted_drink
    })



@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drink-details')
def get_drinks_details(payload):
    '''
    @TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
    '''

    drinks = Drink.query.all()
    formatted_drink = [drink.long() for drink in drinks]
    return jsonify({
        'success':True,
        'drinks': formatted_drink
    })


@app.route("/drinks", methods = ["POST"])
@requires_auth("post:drinks")
def post_drinks(payload):
    '''
    @TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
    '''
    body = request.get_json()
    new_title = body.get("title",None)
    new_recipe = body.get("recipe",None)
    toz =  json.dumps(new_recipe)
    str_recipe = str(toz)
    try:
        drink = Drink(title = new_title,recipe= str_recipe)
        drink.insert()
    except:
        return unprocessable(422)
    return jsonify({
        'Success':True,
        'Drinks': drink.long()
    })




@app.route("/drinks/<drink_id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(token ,drink_id):
    '''
    @TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
    '''
    body = request.get_json()
    drink = Drink.query.get(drink_id)
    if body.get("title"):
        drink.title = body.get("title")
    if body.get("recipe"):
        new_recipe = body.get("recipe")
        new_recipe =  json.dumps(new_recipe)
        str_recipe = str(new_recipe)
        drink.recipe = str_recipe
    drink.update()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route("/drinks/<drink_id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(token, drink_id):
    '''
    @TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    '''
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        "success":True,
        "deleted":drink_id
    })
# Error Handling

# Example error handling for unprocessable entity
@app.errorhandler(422)
def unprocessable(error):
    """Unproccessable error handled"""
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False,
                        "error": 404,
                        "message": "resource not found"
                        }), 404
    @TODO implement error handler for 404
    error handler should conform to general task above
    A HTTP 404 error handled
    '''
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404



@app.errorhandler(AuthError)
def auth_error(error):
    '''
    @TODO implement error handler for AuthError
    error handler should conform to general task above
    '''
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Authorization header is expected."
                    }), 401

@app.errorhandler(403)
def permission_error(error):
    """Catching permission error"""
    return jsonify({
        "success":False,
        "error":403,
        "message": "Not Authorized"
    }), 403
