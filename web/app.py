"""
Web interface for Cannes Slogan Generator
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
from datetime import datetime
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

app = Flask(__name__)

# Load config
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', config=config)


@app.route('/api/info')
def api_info():
    """Get project information"""
    return jsonify({
        'name': 'Cannes Slogan Generator',
        'version': '1.0.0',
        'description': 'Генеративно-аналитический пайплайн для создания 400 оригинальных рекламных слоганов уровня Cannes Lions',
        'features': [
            'LLM генерация с GPT-4/Claude',
            'FAISS векторный поиск',
            'Проверка новизны (embeddings + N-gram)',
            'Качественный скоринг (4 метрики)',
            'Экспорт в JSONL/CSV/TXT'
        ],
        'stats': {
            'corpus_size': '~15,000 слоганов',
            'candidate_pool': '2,500',
            'target_output': '400',
            'languages': ['Russian', 'English']
        }
    })


@app.route('/api/config')
def api_config():
    """Get current configuration"""
    return jsonify({
        'pipeline': config['pipeline'],
        'generation': config['generation'],
        'quality': config['quality'],
        'novelty': config['novelty']
    })


@app.route('/api/examples')
def api_examples():
    """Get example slogans"""
    examples = {
        'ru': [
            {"text": "Думай иначе", "score": 0.85, "style": "минимализм"},
            {"text": "Просто сделай это", "score": 0.90, "style": "повелительное"},
            {"text": "Невозможное возможно", "score": 0.82, "style": "парадокс"},
            {"text": "Время меняться", "score": 0.78, "style": "призыв к действию"},
            {"text": "Будь собой", "score": 0.80, "style": "простота"}
        ],
        'en': [
            {"text": "Think different", "score": 0.90, "style": "minimalism"},
            {"text": "Just do it", "score": 0.95, "style": "imperative"},
            {"text": "Impossible is nothing", "score": 0.88, "style": "paradox"},
            {"text": "Because you're worth it", "score": 0.85, "style": "emotional"},
            {"text": "The ultimate driving machine", "score": 0.82, "style": "metaphor"}
        ]
    }
    return jsonify(examples)


@app.route('/api/stats')
def api_stats():
    """Get pipeline statistics"""
    # Check if there are results
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'out')
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    
    stats = {
        'has_results': False,
        'files': []
    }
    
    # Check for output files
    if os.path.exists(out_dir):
        for filename in ['cannes_400.jsonl', 'cannes_400.csv', 'cannes_400.txt']:
            filepath = os.path.join(out_dir, filename)
            if os.path.exists(filepath):
                stats['files'].append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
                stats['has_results'] = True
    
    # Check for logs
    log_file = os.path.join(logs_dir, 'run.json')
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            stats['last_run'] = json.load(f)
    
    return jsonify(stats)


@app.route('/api/download/<filename>')
def api_download(filename):
    """Download result file"""
    allowed_files = ['cannes_400.jsonl', 'cannes_400.csv', 'cannes_400.txt']
    
    if filename not in allowed_files:
        return jsonify({'error': 'File not allowed'}), 403
    
    filepath = os.path.join(os.path.dirname(__file__), '..', 'out', filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)


@app.route('/api/docs')
def api_docs():
    """Get documentation"""
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    
    return jsonify({'error': 'README not found'}), 404


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
