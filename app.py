from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_file
from flask_socketio import SocketIO
import requests
import json
import os
from dotenv import load_dotenv
from database import init_db, create_session, get_sessions, get_session_messages, add_message, update_session_theme, export_session, delete_session
from prompt_optimizer import PromptOptimizer
import tempfile

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# LMStudio API Konfiguration
LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"

# Initialisiere die Datenbank und Optimizer
init_db()
optimizer = PromptOptimizer()

def generate_streaming_response(messages):
    try:
        # Optimiere den letzten Prompt
        last_message = messages[-1]['content']
        optimized_prompt = optimizer.optimize_prompt(last_message)
        messages[-1]['content'] = optimized_prompt
        
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        response = requests.post(LMSTUDIO_API_URL, 
                               json=payload, 
                               headers=headers, 
                               stream=True)
        
        if response.status_code != 200:
            yield f"data: {json.dumps({'error': 'API-Fehler: ' + str(response.status_code)})}\n\n"
            return

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data.get('choices') and len(data['choices']) > 0:
                            content = data['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                        break

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    sessions = get_sessions()
    return jsonify(sessions)

@app.route('/api/sessions', methods=['POST'])
def new_session():
    data = request.json
    title = data.get('title', 'Neue Chat-Session')
    session_id = create_session(title)
    return jsonify({'session_id': session_id})

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
def remove_session(session_id):
    delete_session(session_id)
    return jsonify({'success': True})

@app.route('/api/sessions/<int:session_id>/messages', methods=['GET'])
def get_messages(session_id):
    messages = get_session_messages(session_id)
    return jsonify(messages)

@app.route('/api/sessions/<int:session_id>/theme', methods=['PUT'])
def set_theme(session_id):
    data = request.json
    theme = data.get('theme')
    if theme in ['light', 'dark']:
        update_session_theme(session_id, theme)
        return jsonify({'success': True})
    return jsonify({'error': 'Ungültiges Theme'}), 400

@app.route('/api/sessions/<int:session_id>/export', methods=['GET'])
def export_chat(session_id):
    format = request.args.get('format', 'json')
    
    if format == 'json':
        data = export_session(session_id)
        if data:
            return Response(
                data,
                mimetype='application/json',
                headers={'Content-Disposition': f'attachment; filename=chat_export_{session_id}.json'}
            )
    
    return jsonify({'error': 'Export fehlgeschlagen'}), 400

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    session_id = data.get('session_id')
    messages = data.get('messages', [])
    
    if session_id:
        # Speichere die Benutzernachricht
        last_message = messages[-1]
        add_message(session_id, last_message['role'], last_message['content'])
    
    return Response(
        stream_with_context(generate_streaming_response(messages)),
        mimetype='text/event-stream'
    )

@app.route('/api/analyze', methods=['POST'])
def analyze_conversation():
    data = request.json
    messages = data.get('messages', [])
    
    # Analysiere den Konversationskontext
    analysis = optimizer.analyze_context(messages)
    
    # Generiere Folgefragen basierend auf der letzten Antwort
    if messages and messages[-1]['role'] == 'assistant':
        followup_questions = optimizer.suggest_followup_questions(messages[-1]['content'])
    else:
        followup_questions = []
    
    # Erstelle eine Zusammenfassung
    summary = optimizer.summarize_conversation(messages)
    
    # Generate visualizations
    conversation_flow = optimizer.generate_conversation_flow(messages)
    knowledge_graph = optimizer.generate_knowledge_graph(messages)
    topic_evolution = optimizer.generate_topic_evolution(messages)
    sentiment_timeline = optimizer.generate_sentiment_timeline(messages)
    
    return jsonify({
        'analysis': analysis,
        'followup_questions': followup_questions,
        'summary': summary,
        'visualizations': {
            'conversation_flow': conversation_flow,
            'knowledge_graph': knowledge_graph,
            'topic_evolution': topic_evolution,
            'sentiment_timeline': sentiment_timeline
        }
    })

@app.route('/api/visualize/flow', methods=['POST'])
def visualize_flow():
    data = request.json
    messages = data.get('messages', [])
    flow = optimizer.generate_conversation_flow(messages)
    return jsonify(flow)

@app.route('/api/visualize/graph', methods=['POST'])
def visualize_graph():
    data = request.json
    messages = data.get('messages', [])
    graph = optimizer.generate_knowledge_graph(messages)
    return jsonify(graph)

@app.route('/api/visualize/topics', methods=['POST'])
def visualize_topics():
    data = request.json
    messages = data.get('messages', [])
    topics = optimizer.generate_topic_evolution(messages)
    return jsonify(topics)

@app.route('/api/visualize/sentiment', methods=['POST'])
def visualize_sentiment():
    data = request.json
    messages = data.get('messages', [])
    sentiment = optimizer.generate_sentiment_timeline(messages)
    return jsonify(sentiment)

@app.route('/api/improve-prompt', methods=['POST'])
def improve_prompt():
    data = request.json
    original_prompt = data.get('prompt', '')
    
    if not original_prompt:
        return jsonify({'error': 'Kein Prompt angegeben'}), 400
    
    improved_prompt = optimizer.optimize_prompt(original_prompt)
    return jsonify({
        'improved_prompt': improved_prompt
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
