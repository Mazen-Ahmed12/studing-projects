# app.py
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"task {self.id}"


@app.route("/", methods=["POST", "GET"])
def hello_world():
    if request.method == "POST":
        task_content = request.form["content"]
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(e)
            return f"There was an issue adding your task {e}"
    else:
        tasks = Todo.query.order_by(Todo.created).all()
        return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:id>")
def delete(id: int):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        print(e)
        return f"There was an issue deleting your task {e}"


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id: int):
    update_task = Todo.query.get_or_404(id)
    if request.method == "POST":
        update_task.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(e)
            return f"There was an issue updating your task {e}"
    else:
        return render_template("update.html", task=update_task)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
