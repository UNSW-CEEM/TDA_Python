from flask import Flask, render_template, request, jsonify
import os
from pyfladesk import init_gui
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if getattr(sys, 'frozen', False):
    template_folder = resource_path('templates')
    static_folder = resource_path('static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


# Here you go to http://127.0.0.1:5000/
@app.route('/')
def index():
    return render_template('index.html', my_name="Nick")


# Here you go to http://127.0.0.1:5000/data
@app.route('/data')
def data():
    return jsonify(
        {'data': [1, 2, 3, 4, 5]}
    )


if __name__ == '__main__':
    # app.run(debug=True)

    init_gui(app, width=500, height=400, window_title='TDA')  # This one runs it as a standalone app