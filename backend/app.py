from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from AI.colorize import predict_emotion
from AI.nlp_model import summarize
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai
import time
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_cors import CORS


# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    diaries = db.relationship('Diary', backref='user', lazy=True)

class Diary(db.Model):
    __tablename__ = 'diary'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String, nullable=False)  # 줄글 or 채팅
    content = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.JSON, nullable=False)
    color = db.Column(db.JSON, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# OpenAI API 키 설정
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Custom GPT ID 설정
custom_gpt_id = os.getenv('CUSTOM_GPT_ID')



# 감정 분석 & 문장 요약
def emotion_analysis(input_text):
    emotion_percentages, mixed_color = predict_emotion(input_text)
    summary = summarize(input_text)
    
    return emotion_percentages, mixed_color, summary

# 대화 기다리기
def wait_on_run(run, thread_id):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(0.2)
    return run


#API
@app.route('/')
def index():
    return render_template('front.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'status': 'failed', 'message': 'Username already exists'})

    password_hash = generate_password_hash(password)
    new_user = User(username=username, password=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        status = 'success'
        message = 'Login successful'
    else:
        status = 'failed'
        message = 'Invalid username or password'

    return jsonify({'status': status, 'message': message, 'user_id': user.id})


# 일기 작성
@app.route('/create', methods=['POST'])
def create():
    data = request.get_json()
    content = data['content']
    user_id = data['user_id']
    type = data['type']

    emotion_percentages, mixed_color, summary = emotion_analysis(content)

    new_diary = Diary(
        user_id=user_id,
        type=type,
        content=content,
        emotion=emotion_percentages,
        color=mixed_color,
        summary=summary
    )
    db.session.add(new_diary)
    db.session.commit()
    return jsonify({'emotion_percentages': emotion_percentages, 'mixed_color': mixed_color, 'summary': summary})


# 일기 정보 불러오기
@app.route('/read', methods=['GET'])
def read():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'status': 'failed', 'message': 'User ID is required'})
    
    try:
        diaries = Diary.query.filter_by(user_id=user_id).all()
        if not diaries:
            return jsonify({'status': 'failed', 'message': 'No diaries found for this user'})

        diary_list = []
        for diary in diaries:
            diary_data = {
                'id': diary.id,
                'type': diary.type,
                'content': diary.content,
                'emotion': diary.emotion,
                'color': diary.color,
                'summary': diary.summary,
                'created_at': diary.created_at
            }
            diary_list.append(diary_data)
        
        return jsonify({'status': 'success', 'diaries': diary_list})
    except Exception as e:
        return jsonify({'status': 'failed', 'message': str(e)})
    

# 커스텀 챗봇 수행
assistant = client.beta.assistants.retrieve(custom_gpt_id) 

# 대화 시작
@app.route('/start_conversation', methods=['GET'])
def start_conversation():
    try:
        print(assistant)
        # 새로운 스레드 생성
        thread = client.beta.threads.create() # 대화를 시작할 때마다 새로운 대화 스레드 생성
        return jsonify({'thread_id': thread.id})
    except openai.error.OpenAIError as e:
        return jsonify({'error': str(e)})


# 대화 도중
@app.route('/chat_response', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    thread_id = data["thread_id"]
    username = data["username"]
    
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant.id,
        instructions=f"사용자를 {username}님이라고 부르세요"
    )
    
    run = wait_on_run(run, thread_id)
    messages = client.beta.threads.messages.list(
        thread_id=thread_id, order="asc", after=message.id
    )
    
    for message in messages.data:
        for content_block in message.content:
            if content_block.type == 'text':
                value = content_block.text.value

    return jsonify({'message': value})


# 대화 종료 -> 사용자 대답 모아서 감정 분석
@app.route('/end_conversation', methods=['POST'])
def end_conversation():
    data = request.get_json()
    thread_id = data['thread_id']
    
    messages = client.beta.threads.messages.list(
        thread_id=thread_id, 
        order="asc"
    )
    
    user_messages = []
    for message in messages.data:
        if message.role == 'user':
            user_messages.append(" ".join(content_block.text.value for content_block in message.content if content_block.type == 'text'))
    
    combined_text = " ".join(user_messages)
    
    emotion_percentages, mixed_color, summary = emotion_analysis(combined_text)
    return jsonify({'input_text': combined_text, 'emotion_percentages': emotion_percentages, 'mixed_color': mixed_color, 'summary': summary})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
