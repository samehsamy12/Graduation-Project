from app import create_app

app = create_app()


@app.route('/static/horse_images/<path:filename>')
def serve_static_horse_image(filename):
    from flask import send_from_directory
    return send_from_directory('static/horse_images', filename)

@app.route('/test-static')
def test_static():
    from flask import send_from_directory
    return send_from_directory('static/horse_images', 'test.txt')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
