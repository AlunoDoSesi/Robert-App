from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, current_app, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = BASE_DIR / "data" / "achados.db"
DEFAULT_UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_MIMETYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-chave-achai-mude-em-producao"),
        DATABASE=str(DEFAULT_DATABASE),
        UPLOAD_FOLDER=str(DEFAULT_UPLOAD_FOLDER),
        MAX_CONTENT_LENGTH=MAX_IMAGE_SIZE,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def close_db(_error: BaseException | None = None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.template_filter("format_datetime")
    def format_datetime(value: str) -> str:
        try:
            date_value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return date_value.strftime("%d/%m/%Y às %H:%M")
        except (TypeError, ValueError):
            return value

    @app.context_processor
    def inject_globals() -> dict:
        return {"site_name": "AchaAí"}

    @app.get("/")
    def index():
        filter_type = request.args.get("tipo", "todos").lower()
        if filter_type not in {"todos", "perdido", "encontrado"}:
            filter_type = "todos"

        search_term = request.args.get("q", "").strip()
        db = get_db()
        items = list_items(db, filter_type, search_term)
        stats = {
            "total": count_items(db),
            "perdidos": count_items(db, "perdido"),
            "encontrados": count_items(db, "encontrado"),
            "resolvidos": count_items(db, status="resolvido"),
        }

        return render_template(
            "index.html",
            items=items,
            filter_type=filter_type,
            search_term=search_term,
            stats=stats,
        )

    @app.route("/cadastrar", methods=["GET", "POST"])
    def create_item():
        if request.method == "GET":
            return render_template("form.html")

        item_type = request.form.get("tipo", "").strip().lower()
        name = request.form.get("nome", "").strip()
        description = request.form.get("descricao", "").strip()
        location = request.form.get("local", "").strip()
        contact = request.form.get("contato", "").strip()
        image = request.files.get("imagem")

        errors = []
        if item_type not in {"perdido", "encontrado"}:
            errors.append("Escolha se o item foi perdido ou encontrado.")
        if not name:
            errors.append("Informe o nome do item.")
        if not description:
            errors.append("Descreva o item para facilitar a identificação.")
        if not location:
            errors.append("Informe o local relacionado ao item.")
        if not contact:
            errors.append("Informe um contato para retorno.")

        image_filename = None
        if image and image.filename:
            original_name = secure_filename(image.filename)
            extension = Path(original_name).suffix.lower().lstrip(".")
            if not original_name or extension not in ALLOWED_EXTENSIONS:
                errors.append("A imagem deve estar nos formatos PNG, JPG, GIF ou WEBP.")
            elif image.mimetype and image.mimetype not in ALLOWED_MIMETYPES:
                errors.append("O tipo de arquivo enviado não é uma imagem válida.")
            else:
                image_filename = f"{uuid.uuid4().hex}.{extension}"

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("form.html"), 400

        if image and image_filename:
            image.save(Path(app.config["UPLOAD_FOLDER"]) / image_filename)

        db = get_db()
        db.execute(
            """
            INSERT INTO items (item_type, name, description, location, contact, image_filename)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item_type, name, description, location, contact, image_filename),
        )
        db.commit()
        flash("Item publicado no mural. Boa sorte na devolução!", "success")
        return redirect(url_for("index"))

    @app.post("/itens/<int:item_id>/resolver")
    def resolve_item(item_id: int):
        db = get_db()
        item = db.execute("SELECT status FROM items WHERE id = ?", (item_id,)).fetchone()
        if item is None:
            flash("Não encontramos esse item no mural.", "error")
            return redirect(url_for("index"))

        next_status = "ativo" if item["status"] == "resolvido" else "resolvido"
        resolved_at = None if next_status == "ativo" else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE items SET status = ?, resolved_at = ? WHERE id = ?",
            (next_status, resolved_at, item_id),
        )
        db.commit()

        if next_status == "resolvido":
            flash("Aviso marcado como resolvido. Obrigado por ajudar!", "success")
        else:
            flash("Aviso reaberto e visível novamente no mural.", "info")
        return redirect(request.referrer or url_for("index"))

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_error: RequestEntityTooLarge):
        flash("A imagem ultrapassa o limite de 5 MB.", "error")
        return render_template("form.html"), 413

    return app


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db() -> None:
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK (item_type IN ('perdido', 'encontrado')),
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            contact TEXT NOT NULL,
            image_filename TEXT,
            status TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'resolvido')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT
        );
        """
    )
    db.commit()


def list_items(db: sqlite3.Connection, filter_type: str, search_term: str) -> list[sqlite3.Row]:
    conditions = ["1 = 1"]
    values: list[str] = []

    if filter_type != "todos":
        conditions.append("item_type = ?")
        values.append(filter_type)

    if search_term:
        conditions.append(
            "(name LIKE ? OR description LIKE ? OR location LIKE ? OR contact LIKE ?)"
        )
        search_value = f"%{search_term}%"
        values.extend([search_value] * 4)

    query = f"""
        SELECT *
        FROM items
        WHERE {' AND '.join(conditions)}
        ORDER BY CASE status WHEN 'ativo' THEN 0 ELSE 1 END, created_at DESC
    """
    return db.execute(query, values).fetchall()


def count_items(
    db: sqlite3.Connection,
    item_type: str | None = None,
    status: str | None = None,
) -> int:
    conditions = ["1 = 1"]
    values: list[str] = []
    if item_type:
        conditions.append("item_type = ?")
        values.append(item_type)
    if status:
        conditions.append("status = ?")
        values.append(status)
    row = db.execute(
        f"SELECT COUNT(*) AS total FROM items WHERE {' AND '.join(conditions)}", values
    ).fetchone()
    return int(row["total"])


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
