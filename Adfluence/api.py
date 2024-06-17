from flask import Flask
from flask_restful import Resource, Api


class Influencer(Resource):
    def get(self):
        return {'hello': 'world'}

