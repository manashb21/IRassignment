from flask import Flask, render_template, request
import logic_search as ls

app = Flask(__name__)

@app.route('/')


def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    final_list = ls.exec_logic(query)
    # Process the search query and perform search operations here
    return render_template('index.html', query=query, final_list = final_list)

if __name__ == '__main__':
    app.run(debug=True)