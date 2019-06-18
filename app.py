from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
api = Api(app)
app.secret_key= 'jose'

jwt = JWT(app, authenticate, identity) # /auth

items = []


# If you are using flask restful dont have to use jsonify
class Item(Resource):

    @jwt_required()
    def get(self, name):

        # next() shows the first item of the filter function
        # If the next function wont findd a item it will return None
        item = next(filter(lambda x: x['name'] == name, items), None)

        return {'item': item }, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': 'An item with name "{}" already exists'.format(name)}, 400

        parser = reqparse.RequestParser()
        parser.add_argument('price',
            type=float,
            required=True,
            help="This field could not be blank"
        )
        # force=True means that it does not look for the content type header
        # otherwise it looks for the header if it doesnt find application/json 
        # it wont do nothing, also can do silent=True to do the same
        # data = request.get_json()
        data = parser.parse_args()
        item = {
            "name": name,
            "price": data['price']
        }
        items.append(item)

        return item, 201

    def delete(self, name):

        global items

        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': 'Item deleted'}

    def put(self, name):
        # Parser adds validation control over json inputs
        # If you dont declare the field in the parser the
        # field does not exist, even if it is included in 
        # json. The regular method get_json() does not allow
        # to do this.
        parser = reqparse.RequestParser()
        parser.add_argument('price',
            type=float,
            required=True,
            help="This field cannot be left blank"
        )
        # data = request.get_json()
        data = parser.parse_args()
        item = next(filter(lambda x:x['name'] == name, items), None)
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
        else:
            item.update(data)

        return item 

class ItemList(Resource):

    def get(self):

        return {'items': items}



api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=5000, debug=True) # HTML pages on error when debug=True

