from database import db
import uuid

class Dataset(db.Model):
    __tablename__ = "datasets"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255))
    uri = db.Column(db.Text)
    description = db.Column(db.Text)


class Column(db.Model):
    __tablename__ = "columns"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = db.Column(db.String, db.ForeignKey("datasets.id"))
    column_name = db.Column(db.String(255))
    data_type = db.Column(db.String(50))
    is_nullable = db.Column(db.Boolean)


class Run(db.Model):
    __tablename__ = "runs"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_name = db.Column(db.String(255))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50))


class LineageEdge(db.Model):
    __tablename__ = "lineage_edges"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_dataset_id = db.Column(db.String)
    target_dataset_id = db.Column(db.String)
    run_id = db.Column(db.String)
    edge_type = db.Column(db.String(50))


class ColumnStatistics(db.Model):
    __tablename__ = "column_statistics"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    column_id = db.Column(db.String, db.ForeignKey("columns.id", ondelete="CASCADE"))
    run_id = db.Column(db.String, db.ForeignKey("runs.id"))
    null_fraction = db.Column(db.Float)
    distinct_count = db.Column(db.Integer)


class DataQualityResult(db.Model):
    __tablename__ = "data_quality_results"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = db.Column(db.String, db.ForeignKey("runs.id"))
    dataset_id = db.Column(db.String, db.ForeignKey("datasets.id"))
    rule_name = db.Column(db.String(255))
    success = db.Column(db.Boolean)
    observed_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())