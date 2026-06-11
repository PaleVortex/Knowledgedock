"""Simple Flask-based backend for Knowledgedock

This module exposes a basic REST API for managing bookmarks, projects,
resources, etc. It reuses the same database manager classes from the
application so the GUI can either use the database directly or communicate
with the server over HTTP. The server can be run standalone or spun up in a
background thread by the GUI.
"""

from threading import Thread
from typing import Any

from flask import Flask, jsonify, request, abort
from flask_cors import CORS

"""Import only the classes actually defined in their respective modules."""
from database import DatabaseManager, BookmarkManager
from research_managers import ProjectManager, TagManager, AnnotationManager

# initialize database and managers (shared with GUI)
db_manager = DatabaseManager()
bookmark_mgr = BookmarkManager(db_manager.db_path)
project_mgr = ProjectManager(db_manager.db_path)
tag_mgr = TagManager(db_manager.db_path)
annotation_mgr = AnnotationManager(db_manager.db_path)

app = Flask(__name__)
CORS(app)  # allow cross-origin requests from GUI if necessary

# --- Helper util ---
def serialize_bookmark(row: Any) -> dict:
    # row order: id, title, url, source, resource_type, added_date, cover_url, description
    return {
        'id': row[0],
        'title': row[1],
        'url': row[2],
        'source': row[3],
        'resource_type': row[4],
        'added_date': row[5],
        'cover_url': row[6],
        'description': row[7],
    }

# --- Bookmarks API ---
@app.route('/api/bookmarks', methods=['GET'])
def list_bookmarks():
    rows = bookmark_mgr.get_all_bookmarks()
    return jsonify([serialize_bookmark(r) for r in rows])

@app.route('/api/bookmarks', methods=['POST'])
def create_bookmark():
    data = request.get_json(force=True)
    if not data or 'title' not in data or 'url' not in data:
        abort(400, 'title and url required')
    success = bookmark_mgr.add_bookmark(
        data['title'], data['url'],
        source=data.get('source', ''),
        resource_type=data.get('resource_type', ''),
        cover_url=data.get('cover_url', ''),
        description=data.get('description', ''),
    )
    if not success:
        abort(400, 'could not create bookmark (may already exist)')
    # Fetch the newly created bookmark to return its ID
    rows = bookmark_mgr.get_all_bookmarks()
    newly_added = next((r for r in rows if r[1] == data['title']), None)
    if newly_added:
        return jsonify({'id': newly_added[0], 'status': 'ok'}), 201
    return jsonify({'status': 'ok'}), 201

@app.route('/api/bookmarks/<int:bookmark_id>', methods=['DELETE'])
def delete_bookmark(bookmark_id: int):
    # first fetch url by id
    rows = bookmark_mgr.get_all_bookmarks()
    target = next((r for r in rows if r[0] == bookmark_id), None)
    if not target:
        abort(404)
    bookmark_mgr.remove_bookmark(target[2])
    return jsonify({'status': 'deleted'})

# --- Projects, tags, annotations can be added similarly as needed ---

# minimal run function

def run(host: str = '127.0.0.1', port: int = 5000, debug: bool = False) -> None:
    """Run the Flask server. This call blocks unless run in a thread."""
    app.run(host=host, port=port, debug=debug, threaded=True)


def start_in_thread(host: str = '127.0.0.1', port: int = 5000, debug: bool = False) -> Thread:
    """Start the backend in a daemon thread and return the thread object."""
    thread = Thread(target=run, args=(host, port, debug), daemon=True)
    thread.start()
    return thread


if __name__ == '__main__':
    print('Starting backend server...')
    run(debug=True)