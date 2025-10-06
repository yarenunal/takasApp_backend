from flask import Blueprint, jsonify
from models.category import Category

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200

@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get specific category by ID"""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    return jsonify({
        'category': category.to_dict()
    }), 200
