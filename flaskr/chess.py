import collections
import functools
from time import strftime
from collections import OrderedDict

import berserk
import chess
import chess.pgn
import berserk

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('chess', __name__)


@bp.route('/load_game',  methods=('GET', 'POST'))
@login_required
def load_game():
    token = 'lip_oI6GmlG6daxtc8OOMWBh'
    session = berserk.TokenSession(token)
    client = berserk.Client(session=session)
    user_games = {}
    count = 0
    formatted_games = None

    fen = "2k4r/ppp2ppp/4b3/4n3/4n3/P1P5/2PrBPPP/R4K1R b - - 1 14"
    # board = chess.Board.set_fen(fen)

    if request.method == 'POST':
        username = request.form['username']
        error = None

        if not username:
            error = 'Username is required.'

        if error is not None:
            flash(error)
        else:
            try:
                db = get_db()
                # db.execute("DELETE FROM carsonmiller")

                if not table_exists(username):

                    query = 'CREATE TABLE {}(id CHAR(15), UNIQUE(id))'.format(username)
                    db.execute(query)

                    for game in client.games.export_by_player(username, max=10):
                        user_games[count] = [game]
                        insert_query = "INSERT INTO {} (id) VALUES (?)".format(username)
                        db.execute(insert_query, (game['id'],))
                        count += 1

                db.commit()
            except Exception:
                error = f"User {username} is invalid."
                flash(error)

            return redirect(url_for('chess.games', username=username))
    return render_template('chess/load_game.html')


@bp.route('/games')
@login_required
def games():
    username=request.args.get('username')
    links = []
    db = get_db()
    query = 'SELECT * FROM {}'.format(username)

    game_list = db.execute(query).fetchall()

    for game_id in game_list:
        links.append(game_id[0])
        # links.append("https://lichess.org/embed/{}?theme=auto&bg=auto".format(game_id[0]))

    return render_template('chess/games.html', links=links)


def table_exists(user):
    db = get_db()
    query = """SELECT name FROM sqlite_master WHERE type='table' AND name ='{}'""".format(user)
    result = db.execute(query).fetchall()

    # Will be > 0 if table exists
    return not result == []


@bp.route('/analysis')
@login_required
def analysis():
    id = request.args.get('id')
    return render_template('chess/analysis.html', id=id)


@bp.route('/players',  methods=('GET', 'POST'))
@login_required
def players():
    if request.method == 'POST':
        player = request.form['player']

        try:
            db = get_db()
            db.session.add(player)
            db.commit()
            return redirect(url_for('chess.players'))
        except Exception:
            return "Could not add player."
    else:
        return render_template('chess/players.html')
