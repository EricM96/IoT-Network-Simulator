from flask import Flask, render_template, make_response, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root_controller():
    if request.method == 'POST':
        print(request.form, flush=True)
    return make_response(render_template(
        'index.html'
    ))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
