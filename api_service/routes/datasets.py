from flask import Blueprint, request, jsonify
from models import Dataset, Column
from database import db
from marshmallow import Schema, fields, ValidationError

import uuid

class ColumnSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True)

class DatasetSchema(Schema):
    name = fields.Str(required=True)
    uri = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    schema = fields.List(fields.Nested(ColumnSchema))

dataset_schema = DatasetSchema()

datasets_bp = Blueprint("datasets", __name__)

@datasets_bp.route("/datasets", methods=["POST"])
def create_dataset():
    data = request.json

    try:
        validated_data = dataset_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    dataset_id = str(uuid.uuid4())

    try:
        dataset = Dataset(
            id=dataset_id,
            name=validated_data["name"],
            uri=validated_data["uri"],
            description=validated_data.get("description")
        )
        db.session.add(dataset)

        for col in validated_data.get("schema", []):
            column = Column(
                dataset_id=dataset.id,
                column_name=col["name"],
                data_type=col["type"]
            )
            db.session.add(column)

        db.session.commit()
        return jsonify({"dataset_id": dataset.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@datasets_bp.route("/datasets/<dataset_id>", methods=["GET"])
def get_dataset(dataset_id):

    dataset = Dataset.query.filter_by(id=dataset_id).first()

    if not dataset:
        return jsonify({"error": "Dataset not found"}), 404

    columns = Column.query.filter_by(dataset_id=dataset_id).all()

    schema = []

    for col in columns:
        schema.append({
            "name": col.column_name,
            "type": col.data_type
        })

    return jsonify({
        "id": dataset.id,
        "name": dataset.name,
        "uri": dataset.uri,
        "description": dataset.description,
        "schema": schema
    })
@datasets_bp.route("/datasets/search", methods=["GET"])
def search_datasets():
    query_str = request.args.get("q", "")
    
    if query_str:
        datasets = Dataset.query.filter(Dataset.name.ilike(f"%{query_str}%")).all()
    else:
        datasets = Dataset.query.all()
        
    result = []
    for d in datasets:
        result.append({
            "id": d.id,
            "name": d.name,
            "uri": d.uri,
            "description": d.description
        })

    return jsonify(result), 200