import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Incomplete')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': str(self.due_date),
            'status': self.status
        }


@app.route('/tasks', methods=['POST'])
def create_task():
    with app.app_context():
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        due_date_str = data.get('due_date')
        status = data.get('status', 'Incomplete')

        try:
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Please provide a date in YYYY-MM-DD format.'}), 400

        task = Task(title=title, description=description, due_date=due_date, status=status)
        db.session.add(task)
        db.session.commit()

        return jsonify(task.to_dict()), 201


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        return jsonify(task.to_dict())


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)

        due_date_str = data.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Please provide a date in YYYY-MM-DD format.'}), 400

        task.status = data.get('status', task.status)

        db.session.commit()

        return jsonify(task.to_dict())


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    with app.app_context():
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': 'Task deleted'})


@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    with app.app_context():
        tasks = Task.query.all()

        task_list = [task.to_dict() for task in tasks]
        return jsonify({
            'tasks': task_list,
            'total_items': len(task_list)
        })

@app.route('/tasks/page/<int:page>', methods=['GET'])
def get_tasks_by_page(page):
    with app.app_context():
        per_page = request.args.get('per_page', 5, type=int)

        tasks = Task.query.paginate(page=page, per_page=per_page)

        task_list = [task.to_dict() for task in tasks.items]
        return jsonify({
            'tasks': task_list,
            'current_page': tasks.page,
            'total_pages': tasks.pages,
            'total_items': tasks.total
        })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
