from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import db, Course, User, Flashcard, flashcard_responses
from app.auth import require_role
from sqlalchemy.exc import SQLAlchemyError

api = Blueprint('api', __name__)

@api.route('/courses', methods=['GET'])
@require_role('user')
def get_courses():
    user_email = get_jwt_identity()  
    user = User.query.filter_by(email=user_email).first()
    if user:
        user_id = user.id
        courses = Course.query.filter_by(user_id=user_id).order_by(Course.id.desc()).all()
        courses_data = [
            {
                "id": course.id,
                "title": course.title,
                "includeInRepetitions": course.include_in_repetitions
            }
            for course in courses]
        return jsonify(courses_data), 200
    else:
        return jsonify({"message": "Użytkownik nie znaleziony"}), 404


@api.route('/courses/<int:course_id>', methods=['PUT'])
@require_role('user')
def update_course(course_id):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    data = request.get_json()
    course = Course.query.filter_by(id=course_id, user_id=user.id).first()
    if not course:
        return jsonify({"message": "Kurs nie został znaleziony."}), 404

    course.include_in_repetitions = data.get('includeInRepetitions', course.include_in_repetitions)
    db.session.commit()
    return jsonify({"message": "Kurs został zaktualizowany."}), 200


@api.route('/courses/create', methods=['POST'])
@require_role('user')
def create_course():
    user_email = get_jwt_identity() 
    data = request.get_json()

    if 'title' not in data or not data['title']:
        return jsonify({"msg": "Title is required"}), 400

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    new_course = Course(title=data['title'], user_id=user.id)
    db.session.add(new_course)
    db.session.commit()

    return jsonify({"msg": "Course created successfully", "course_id": new_course.id}), 201


@api.route('/flashcards/create', methods=['POST'])
@require_role('user')
def add_flashcard():
    user_email = get_jwt_identity() 
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    user_id = user.id
    data = request.get_json()
    text = data.get('text')
    language = data.get('language')
    course_id = data.get('course_id')
    response_ids = data.get('response_ids', [])

    if not text or not language or not course_id:
        return jsonify({"msg": "Missing required flashcard data"}), 400

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    new_flashcard = Flashcard(text=text, language=language, course_id=course_id)

    try:
        db.session.add(new_flashcard)
        db.session.flush()

        for response_id in response_ids:
            response_flashcard = Flashcard.query.get(response_id)
            if response_flashcard:
                db.session.execute(flashcard_responses.insert().values(response_direction_a_id=new_flashcard.id, response_direction_b_id=response_id))
                db.session.execute(flashcard_responses.insert().values(response_direction_a_id=response_id, response_direction_b_id=new_flashcard.id))

        db.session.commit()
        return jsonify({"msg": "Flashcard added successfully", "flashcard_id": new_flashcard.id}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to add flashcard", "error": str(e)}), 500



@api.route('/review', methods=['POST'])
@require_role('user')
def review_flashcard():
    pass