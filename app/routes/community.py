from flask import Blueprint, request, jsonify, g, current_app
from app.extensions import db
from app.models.community import Post, Comment, Like
from app.utils.jwt_utils import token_required
from werkzeug.utils import secure_filename
import os
import uuid

community_bp = Blueprint("community", __name__)

# Configure upload folder for posts
POST_UPLOAD_FOLDER = os.path.join('static', 'uploads', 'posts')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@community_bp.route("/community/post", methods=["POST"])
@token_required
def create_post():
    if 'content' not in request.form:
        return jsonify({"message": "Content is required"}), 400

    content = request.form['content']
    image_url = None

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            upload_dir = os.path.join(current_app.root_path, POST_UPLOAD_FOLDER)
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            image_url = f"/{POST_UPLOAD_FOLDER}/{filename}"

    post = Post(user_id=g.user_id, content=content, image_url=image_url)
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created", "post_id": post.id}), 201

@community_bp.route("/community/post/<int:post_id>", methods=["PUT"])
@token_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    if post.user_id != g.user_id:
        return jsonify({"message": "Unauthorized"}), 403

    if 'content' not in request.form:
        return jsonify({"message": "Content is required"}), 400

    content = request.form['content']
    image_url = post.image_url

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            # Delete old image if exists
            if image_url and os.path.exists(os.path.join(current_app.root_path, image_url.lstrip('/'))):
                os.remove(os.path.join(current_app.root_path, image_url.lstrip('/')))
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            upload_dir = os.path.join(current_app.root_path, POST_UPLOAD_FOLDER)
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            image_url = f"/{POST_UPLOAD_FOLDER}/{filename}"
        elif file.filename == '':
            # Remove image if empty file is sent
            if image_url and os.path.exists(os.path.join(current_app.root_path, image_url.lstrip('/'))):
                os.remove(os.path.join(current_app.root_path, image_url.lstrip('/')))
            image_url = None

    post.content = content
    post.image_url = image_url
    db.session.commit()

    return jsonify({"message": "Post updated"}), 200

@community_bp.route("/community/post/<int:post_id>", methods=["DELETE"])
@token_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    if post.user_id != g.user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Delete image if exists
    if post.image_url and os.path.exists(os.path.join(current_app.root_path, post.image_url.lstrip('/'))):
        os.remove(os.path.join(current_app.root_path, post.image_url.lstrip('/')))

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted"}), 200

@community_bp.route("/community/post/<int:post_id>/comment", methods=["POST"])
@token_required
def add_comment(post_id):
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"message": "Content is required"}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    comment = Comment(post_id=post_id, user_id=g.user_id, content=content)
    db.session.add(comment)
    db.session.commit()

    return jsonify({"message": "Comment added", "comment_id": comment.id}), 201

@community_bp.route("/community/post/<int:post_id>/comment/<int:comment_id>", methods=["PUT"])
@token_required
def edit_comment(post_id, comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    if comment.user_id != g.user_id:
        return jsonify({"message": "Unauthorized"}), 403
    if comment.post_id != post_id:
        return jsonify({"message": "Comment does not belong to this post"}), 400

    data = request.json
    content = data.get("content")
    if not content:
        return jsonify({"message": "Content is required"}), 400

    comment.content = content
    db.session.commit()

    return jsonify({"message": "Comment updated"}), 200

@community_bp.route("/community/post/<int:post_id>/comment/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    if comment.user_id != g.user_id:
        return jsonify({"message": "Unauthorized"}), 403
    if comment.post_id != post_id:
        return jsonify({"message": "Comment does not belong to this post"}), 400

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted"}), 200

@community_bp.route("/community/post/<int:post_id>/like", methods=["POST"])
@token_required
def like_post(post_id):
    existing_like = Like.query.filter_by(post_id=post_id, user_id=g.user_id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"message": "Post unliked"}), 200

    like = Like(post_id=post_id, user_id=g.user_id)
    db.session.add(like)
    db.session.commit()

    return jsonify({"message": "Post liked"}), 200

@community_bp.route("/community/feed", methods=["GET"])
def community_feed():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    result = []
    for p in posts:
        result.append({
            "id": p.id,
            "author_id": p.user_id,
            "username": p.user.username,
            "content": p.content,
            "image_url": p.image_url,  # Include image_url
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "likes": len(p.likes),
            "is_liked": Like.query.filter_by(post_id=p.id, user_id=g.user_id if hasattr(g, 'user_id') else None).first() is not None,
            "comments": len(p.comments)
        })

    return jsonify(result), 200

@community_bp.route("/community/post/<int:post_id>", methods=["GET"])
def view_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    return jsonify({
        "id": post.id,
        "author_id": post.user_id,
        "username": post.user.username,
        "content": post.content,
        "image_url": post.image_url,  # Include image_url
        "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
        "likes": len(post.likes),
        "is_liked": Like.query.filter_by(post_id=post.id, user_id=g.user_id if hasattr(g, 'user_id') else None).first() is not None,
        "comments": [
            {
                "id": c.id,
                "user_id": c.user_id,
                "username": c.user.username,
                "content": c.content,
                "created_at": c.created_at.strftime("%Y-%m-%d %H:%M")
            } for c in post.comments
        ]
    }), 200