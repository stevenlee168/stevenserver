from flask import Flask, render_template

app = Flask(__name__)

# Trang chính
@app.route('/')
def index():
    return render_template('index.html')

# Trang tiện ích (utility pages) như lasercutting.html, etc.
@app.route('/utility/<page>')
def utility_page(page):
    try:
        return render_template(f'utility/{page}')
    except:
        return "Unexpected Error", 404

# Chạy server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
