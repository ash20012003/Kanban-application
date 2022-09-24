from flask import request
from flask_restful import Resource, fields, marshal_with
from flask_restful import Api, Resource, fields, marshal_with, reqparse
from flask_restful.representations import json
from werkzeug.exceptions import HTTPException
from main import *

user_resource = {
    "username" : fields.String,
    "count" : fields.Integer,
    "hash" : fields.String
}

table_resource = {
    "todoCount" : fields.Integer,
    "todoHeader" : fields.String,
    "tuserId" : fields.Integer,
    "description" : fields.String
}

list_resource = {
    "list_index" : fields.Integer,
    "list_name" : fields.String,
    "todo_i" : fields.Integer,
    "todo_u" : fields.Integer,
    "start_time" : fields.Integer,
    "end_time" : fields.Integer,
    "completed" : fields.Integer,
    "completed_time" : fields.Integer
}

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('hash')

create_todo_parser = reqparse.RequestParser()
create_todo_parser.add_argument('todoHeader')
create_todo_parser.add_argument('tuserId')
create_todo_parser.add_argument('description')

create_list_parser = reqparse.RequestParser()
create_list_parser.add_argument('list_name')
create_list_parser.add_argument('todo_i')
create_list_parser.add_argument('todo_u')
create_list_parser.add_argument('end_time')
create_list_parser.add_argument('completed')
create_list_parser.add_argument('completed_time')


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        error_json = {"error_code": error_code, 'error_message': error_message}
        self.response = make_response(json.dumps(error_json), status_code)


class InputValidationError(HTTPException):
    def __init__(self, status_code, error_message):
        self.response = make_response(error_message, status_code)


class UserAPI(Resource):
    @marshal_with(user_resource)
    def get(self, count):
        user = db.session.query(AllUser).filter(AllUser.count == count).first()
        if user:
            return user
        else:
            raise InputValidationError(404, 'User not found')
    
    @marshal_with(user_resource)
    def put(self, count):
        args = create_user_parser.parse_args()
        username = args.get('username', None)
        password = args.get('hash', None)
        if username is None or username.isnumeric():
            raise BusinessValidationError(400, 'USER001', 'User Name is required and should be string.')
        user = db.session.query(AllUser).filter(AllUser.count == count)
        if user is None:
            raise InputValidationError(404, 'User not found')
        user.username = username
        user.hash = password
        db.session.add(user)
        db.session.commit()
        return user, 200
    
    def delete(self, count):
        user = db.session.query(AllUser).filter(AllUser.count == count)
        if user:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            cu = db.session.query(CurrentUser).filter(CurrentUser.user_name==username).first()
            cuid = cu.cur_user_id
            if cu:
                db.session.delete(cu)
                db.session.commit()
            th = db.session.query(TodoHeader).filter(TodoHeader.tuserId==cuid).all()
            for t in th:
                db.session.delete(t)
                db.session.commit()
            l = db.session.query(List).filter(List.todo_u==cuid).all()
            for li in l:
                db.session.delete(li)
                db.session.commit()
        else:
            raise InputValidationError(404, 'User not found')
        return "Successfully Deleted", 200 
    
    @marshal_with(user_resource)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get('username')
        password = args.get('hash')
        if username is None or username.isnumeric():
            raise BusinessValidationError(400, 'USER001', 'USer Name is required and should be string.')
        user = db.session.query(AllUser).filter(AllUser.username == username).first()
        if user:
            raise InputValidationError(409, 'user already exist')
        new_user = AllUser(username=username, hash=password)
        db.session.add(new_user)
        db.session.commit()
        if not new_user is None:    
            cu = CurrentUser(user_name = username)
            db.session.add(cu)
            db.session.commit()
        return new_user, 201
    
class TableAPI(Resource):
    @marshal_with(table_resource)
    def get(self, todoCount):
        table = db.session.query(TodoHeader).filter(TodoHeader.todoCount == todoCount).first()
        if table:
            return table
        else:
            raise InputValidationError(404, 'Table not found')
    
    @marshal_with(table_resource)
    def put(self, todoCount):
        args = create_todo_parser.parse_args()
        head = args.get('todoHeader', None)
        id = args.get('tuserId', None)
        desc = args.get('description', None)
        if head is None or head.isnumeric():
            raise BusinessValidationError(400, 'TABLE001', 'Table Name is required and should be string.')
        if desc.isnumeric():
            raise BusinessValidationError(400, 'TABLE002', 'Table Description should be string.')
        table = db.session.query(TodoHeader).filter(TodoHeader.todoCount == todoCount)
        if table is None:
            raise InputValidationError(404, 'Table not found')
        table.todoHeader = head
        table.tuserId = id
        table.description = desc
        db.session.add(table)
        db.session.commit()
        return table, 200
    
    def delete(self, todoCount):
        table = db.session.query(TodoHeader).filter(TodoHeader.todoCount == todoCount)
        if table:
            id = table.tuserId
            db.session.delete(table)
            db.session.commit()
            li = db.session.query(List).filter(List.todo_u==id).all()
            for l in li:
                db.session.delete(l)
                db.session.commit()
        else:
            raise InputValidationError(404, 'Table not found')
        return "Successfully Deleted", 200 
    
    @marshal_with(table_resource)
    def post(self):
        args = create_todo_parser.parse_args()
        head = args.get('todoHeader')
        id = args.get('tuserId')
        desc = args.get('description')
        if head is None or head.isnumeric():
            raise BusinessValidationError(400, 'TABLE001', 'Table Name is required and should be string.')
        if desc.isnumeric():
            raise BusinessValidationError(400, 'TABLE002', 'Table Description should be string.')
        table = db.session.query(TodoHeader).filter(TodoHeader.todoHeader == head).first()
        if table:
            raise InputValidationError(409, 'table already exist')
        new_table = TodoHeader(todoHeader = head, tuserId = id, description = desc)
        db.session.add(new_table)
        db.session.commit()
        return new_table, 201

class ListAPI(Resource):
    @marshal_with(list_resource)
    def get(self, index):
        list = db.session.query(List).filter(List.list_index == index).all()
        if list:
            return list
        else:
            raise InputValidationError(404, 'List not found')
    
    @marshal_with(table_resource)
    def put(self, index):
        args = create_list_parser.parse_args()
        name = args.get('list_name', None)
        id_t = args.get('todo_i', None)
        id_u = args.get('todo_u', None)
        desc = args.get('description', None)
        if head is None or head.isnumeric():
            raise BusinessValidationError(400, 'TABLE001', 'Table Name is required and should be string.')
        if desc.isnumeric():
            raise BusinessValidationError(400, 'TABLE002', 'Table Description should be string.')
        table = db.session.query(TodoHeader).filter(TodoHeader.todoCount == todoCount)
        if table is None:
            raise InputValidationError(404, 'Table not found')
        table.todoHeader = head
        table.tuserId = id
        table.description = desc
        db.session.add(table)
        db.session.commit()
        return table, 200
    
    def delete(self, todoCount):
        table = db.session.query(TodoHeader).filter(TodoHeader.todoCount == todoCount)
        if table:
            id = table.tuserId
            db.session.delete(table)
            db.session.commit()
            li = db.session.query(List).filter(List.todo_u==id).all()
            for l in li:
                db.session.delete(l)
                db.session.commit()
        else:
            raise InputValidationError(404, 'Table not found')
        return "Successfully Deleted", 200 
    
    @marshal_with(table_resource)
    def post(self):
        args = create_todo_parser.parse_args()
        head = args.get('todoHeader')
        id = args.get('tuserId')
        desc = args.get('description')
        if head is None or head.isnumeric():
            raise BusinessValidationError(400, 'TABLE001', 'Table Name is required and should be string.')
        if desc.isnumeric():
            raise BusinessValidationError(400, 'TABLE002', 'Table Description should be string.')
        table = db.session.query(TodoHeader).filter(TodoHeader.todoHeader == head).first()
        if table:
            raise InputValidationError(409, 'table already exist')
        new_table = TodoHeader(todoHeader = head, tuserId = id, description = desc)
        db.session.add(new_table)
        db.session.commit()
        return new_table, 201



