from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify, request

engine = create_engine('sqlite:////home/data/users_result.sqlite', echo=False)
Base = declarative_base()


class User(Base, SerializerMixin):
    __tablename__ = 'users'
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Name = Column(String, nullable=False)
    Surname = Column(String, nullable=False)
    Result = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<User({self.ID}, {self.Name}, {self.Surname}, {self.Rating})>'


class Student(Base, SerializerMixin):
    __tablename__ = 'students'
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Name = Column(String, nullable=False)
    Rus = Column(Integer, nullable=False, default=0)
    Math = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Student({self.ID}, {self.Name}, {self.Rus}, {self.Math})>'


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

app = Flask(__name__)


@app.route('/api/students', methods=['GET'])
def get_students():
    session = Session()
    students = session.query(Student).all()
    return jsonify({'students': [student.to_dict() for student in students]})


@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    session = Session()
    student = session.query(Student).filter(Student.ID == student_id).first()
    if not student:
        return jsonify({'error': 'Not found'})
    return jsonify({'student': student.to_dict()})


@app.route('/api/users', methods=['POST'])
def post_student():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['Name', 'Surname']):
        return jsonify({'error': 'Bad request'})
    if not isinstance(request.json['Name'], str):
        return jsonify({'error': 'Name not str'})
    if not isinstance(request.json['Surname'], str):
        return jsonify({'error': 'Surname not str'})
    session = Session()
    result = 0
    if 'Key1' in request.json:
        if not isinstance(request.json['Key1'], int):
            return jsonify({'error': 'Key1 not int'})
        student = session.query(Student).filter(Student.ID == 7).first()
        if student and student.Math == request.json['Key1']:
            result += 1
    if 'Key2' in request.json or 'Key3' in request.json:
        rus_list = []
        math_list = []
        sum_list = []
        students = session.query(Student).all()
        for student in students:
            rus_list.append(student.Rus)
            math_list.append(student.Math)
            sum_list.append(student.Rus + student.Math)
        if 'Key2' in request.json:
            if not isinstance(request.json['Key2'], int):
                return jsonify({'error': 'Key2 not int'})
            if max(sum_list) == request.json['Key2']:
                result += 1
        if 'Key3' in request.json:
            if not isinstance(request.json['Key3'], int):
                return jsonify({'error': 'Key3 not int'})
            if sum(rus_list) // len(rus_list) == request.json['Key3']:
                result += 1

    user = User(
        Name=request.json['Name'],
        Surname=request.json['Surname'],
        Result=result
    )
    session.add(user)
    session.commit()
    return jsonify({'success': 'OK', 'result': result})


if __name__ == '__main__':
    app.run()
