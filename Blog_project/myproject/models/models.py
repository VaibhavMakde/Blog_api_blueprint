from ..extensions import db, ma


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    blogs = db.relationship('Blog', backref='user')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'blog.id', ondelete="CASCADE"), nullable=False)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    blog = db.Column(db.String(500))
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='blog')


######################    MODELS SCHEMA USING MARSHMALLOW HERE  ########################################

class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comment
        load_instance = True
        include_relationships = True
        fields = ('id', 'text', 'author', 'post_id')
        # include_fk = True


class BlogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blog
        ordered = False
        load_instance = True
        include_relationships = True

        fields = ('id', 'title', 'blog', 'author', 'comments')

    comments = ma.Nested(CommentSchema, many=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_relationships = True
        fields = ('id', 'public_id', 'username', 'admin')


