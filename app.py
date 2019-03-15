from flask import Flask
from flask_restplus import Resource, Api, fields
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Student Tracker',
    description='Tracking student grades'
)

ns = api.namespace('student', description='student operations')

# Models
SubjectModel = api.model('Subject', {
    'id': fields.Integer(readOnly=True, description='The subject unique identifier'),
    'name': fields.String(required=False, description='The subject name'),
    'grade': fields.Integer(readOnly=False, description='The subject grade'),
})

StudentModel = api.model('Student', {
    'id': fields.Integer(readOnly=True, description='The student unique identifier'),
    'name': fields.String(required=False, description='The student name'),
    'subjects': fields.List(fields.Nested(SubjectModel), description='List of subjects'),
})

# Data Access Object (DAO)


class StudentDAO(object):
    def __init__(self):
        self.counter = 0
        self.students = list()

    def get(self, _id):
        for student in self.students:
            if student['id'] == _id:
                return student
        api.abort(404, "Student {} doesn't exist".format(_id))

    def create(self, data):
        student = data
        student['id'] = self.counter = self.counter + 1
        self.students.append(student)
        return student

    def update(self, _id, data):
        student = self.get(_id)
        student.update(data)
        return student


class SubjectDAO(object):
    def __init__(self):
        self.counter = 0
        self.subjects = list()

    def get(self, _id):
        for subject in self.subjects:
            if subject['id'] == _id:
                return subject
        api.abort(404, "Subject {} doesn't exist".format(_id))

    def create(self, data):
        subject = data
        subject.id = self.counter = self.counter + 1
        self.subjects.append(subject)
        return subject

    def update(self, _id, data):
        subject = self.get(_id)
        subject.update(data)
        return subject

DAO_student = StudentDAO()
DAO_subject = SubjectDAO()


# SERVICES
@ns.route('/')
class ListStudentsService(Resource):
    '''Shows a list of all Students, and lets you add (POST) a new student'''
    @ns.doc('list_students')
    @ns.marshal_list_with(StudentModel)
    def get(self):
        return DAO_student.students

    @ns.doc('create_student')
    @ns.expect(StudentModel)
    @ns.marshal_with(StudentModel, code=201)
    def post(self):
        '''Create a new student'''
        return DAO_student.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Student is not found')
@ns.param('id', 'The student identifier')
class Student(Resource):
    '''Show a single student '''
    @ns.doc('get_student')
    @ns.marshal_with(StudentModel)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO_student.get(id)

    @ns.expect(StudentModel)
    @ns.marshal_with(StudentModel)
    def put(self, id):
        '''Update a student give their identifier'''
        return DAO_student.update(id, api.payload)


def average_grade(student):
    '''
    :param student: the student model
    :return: calculated average grade of all subjects
    '''
    if len(student.subjects) == 0:
        return 0

    grade_total = 0
    for subject in student.subjects:
        grade_total += subject.grade

    return grade_total / len(student.subjects)


if __name__ == '__main__':
    app.run(debug=True)

