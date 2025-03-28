from flask import Flask, render_template

app = Flask(__name__, template_folder='presentation/templates')
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')


@app.route('/')
def index():
    return render_template('index.pug')


@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.pug')


if __name__ == '__main__':
    app.run()
