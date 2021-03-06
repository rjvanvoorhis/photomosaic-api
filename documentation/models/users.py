from flask_restplus import fields, Model

metadata = Model('metadata', {
    'commenter_id': fields.String,
    'date': fields.String,
})

comment_model = Model('comment_model', {
    'metadata': fields.Nested(metadata),
    'comment': fields.String
})

gallery_item = Model('gallery_item', {
    'username': fields.String,
    'mosaic_url': fields.String,
    'thumbnail_url': fields.String,
    'alternate_url': fields.String,
    'alternate_thumbnail_url': fields.String,
    'gallery_id': fields.String,
    'toggle_on': fields.Boolean,
    'is_visible': fields.Boolean,
    'comments': fields.List(fields.Nested(comment_model))
})

upload_img = Model('upload', {
    'img_path': fields.Url
})

post_response = Model('uploadResponse', {
    'file_id': fields.String,
    'thumbnail_id': fields.String,
    'img_path': fields.String
})

message_model = Model('message_item', {
  "original_file": fields.String(example="examples/mifune.jpg"),
  "frame_directory": fields.String(example="examples/Mosaic_of_mifune"),
  "output_file": fields.String(example="examples/Mosaic_of_mifune.jpg"),
  "gif_name": fields.String(example="examples/Mosaic_of_mifune.gif"),
  "current": fields.String(example="examples/mifune.jpg"),
  "is_animated": fields.Boolean,
  "status": fields.String(example="queued"),
  "expire_at": fields.Float(example=1543896087.8349004),
  "message_id": fields.String(example="515a5393-1d38-4f03-bf0c-b9ddba4255b9"),
  "total_frames": fields.Integer(example=50),
  "progress": fields.Float(example=0.0)
})

message_post = Model('message_post', {
    'path': fields.String(example='examples/mifune.jpg'),
    'enlargement': fields.Float(example=1.0),
    'tile_size': fields.Integer(example=8),
    'method': fields.String(example='euclid'),
    'img_type': fields.String(example='L'),
    'max_repeats': fields.Integer(example=0),
    'mode': fields.String(example='I'),
    'frame_duration': fields.Float(example=0.1),
    'tile_rescale': fields.Float(example=1.0),
    'threads': fields.Integer(example=3),
})

friend_model = Model('friend', {
    'friend_id': fields.String,
    'date': fields.String,
})

user_model = Model('user', {
    'username': fields.String,
    'password': fields.String,
    '_id': fields.String,
    'roles': fields.List(fields.String),
    'gallery': fields.List(fields.Nested(gallery_item)),
    'uploads': fields.List(fields.Nested(post_response)),
    'friends': fields.List(fields.Nested(friend_model)),
    'messages': fields.List(fields.Nested(message_model)),
    'email': fields.String
})