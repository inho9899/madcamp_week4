from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from models.nlp_model import nlp_model_predict, summarize, keyword, generate_keywords  # 수정된 부분
from kobert_transformers import get_kobert_model
from kobert_tokenizer import KoBERTTokenizer
from backend.AI.colorize import BERTClassifier, predict_emotion
import torch
from torch import nn
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_text = db.Column(db.String(500))
    output_text = db.Column(db.String(500))

    def __init__(self, input_text, output_text):
        self.input_text = input_text
        self.output_text = output_text
        

# AI Package
model_save_path = 'AI/saved_model'
tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
bertmodel = get_kobert_model()
model = BERTClassifier(bertmodel, dr_rate=0.5).to('cuda')
model.load_state_dict(torch.load(os.path.join(model_save_path, 'pytorch_model.bin')))


#API 생성
@app.route('/')
def index():
    return render_template('front.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_text = data['input_text']
    
    emotion_percentages, mixed_color = predict_emotion(input_text, model, tokenizer)
    print(emotion_percentages)
    print(mixed_color)
    # output_text = summarize(input_text)
    # output_text = keyword(input_text)
    # output_text = generate_keywords(input_text)

    
    # new_prediction = Prediction(input_text=input_text, output_text=output_text)
    # db.session.add(new_prediction)
    # db.session.commit()
    return jsonify({'input_text': input_text, 'emotion_percentages': emotion_percentages, 'mixed_color': mixed_color})

if __name__ == '__main__':
    app.run(debug=True)
