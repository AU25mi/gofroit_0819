# flaskモジュールからFlaskクラスをインポート
from flask import Flask, render_template, request, redirect, session
# sqlite3とdatetimeをインポート
import sqlite3, datetime

# Flaskクラスをインスタンス化してapp変数に代入
app = Flask(__name__)

# セッション情報を暗号化するためのkey
app.secret_key = "sunabacogoforit20230818"

# データベースとのやりとりは関数を定義してその関数を実行
# データベースのファイル名
db_file = "goforit.db"

# トップページの表示
@app.route("/")
def index():
    if "user_id" in session and "page" in session:
        # セッション情報があればリスト表示
        page = session["page"]
        return redirect("/list/" + page)
    else:
        # セッション情報が無ければトップページを表示
        return render_template("index.html")

# ログインを実行
@app.route("/login", methods=["POST"])
def login_post():
    # フォームからログイン情報取得
    name = request.form.get("name")
    password = request.form.get("password")
    
    # データベースへ接続とログイン情報の確認
    id = get_list(db_file,"SELECT id FROM users WHERE user_name = ? AND password = ?",(name, password), False)
    if id is None:
        # idがなければトップページにリダイレクト
        return redirect("/")
    else:
        # idがあればセッションを発行してidと表示順を格納
        session["user_id"] = id
        session["page"] = "regist"
        # idがあれば登録順リストのページにリダイレクト
        return redirect("/list/regist")

# 新規ユーザー登録ページの表示
@app.route("/regist")
def regist():
    if "user_id" in session and "page" in session:
        # セッション情報があればリスト表示
        page = session["page"]
        return redirect("/list/" + page)
    else:
        # セッション情報が無ければ新規ユーザー登録ページを表示
        return render_template("regist.html")

# 新規ユーザー登録の実行
@app.route("/regist", methods = ["POST"])
def regist_post():
    # フォームから登録情報（ユーザー名とパスワード）を取得
    name = request.form.get("name")
    password = request.form.get("password")

    if name == '' or password == '':
        # ユーザー名とパスワードのどちらかが空欄であればregistにリダイレクト
        return redirect("/regist")
    
    # usersテーブルに新規ユーザー情報のレコードを追加
    add_record(db_file, "INSERT INTO users values(null, ? , ?)", (name, password))

    # 追加されたユーザー情報からユーザーのIDを取得
    id = get_list(db_file, "SELECT id FROM users WHERE user_name = ? AND password = ?", (name, password), False)
    if id is None:
        # idが存在しなければトップページにリダイレクト
        return redirect("/")
    else:
        # idがあればセッションを発行してidと表示順を格納
        session["user_id"] = id
        session["page"] = "regist"
        # idがあれば登録順リストのページにリダイレクト
        return redirect("/list/regist")

# リストのページ表示
# orderに登録順といいね順のどちらか格納
# top_good:いいねトップの言葉を格納
# word_list:登録済みの言葉のリストを格納
@app.route("/list/<order>")
def list_get(order):
    # セッション内にuser_idがあれば（ログイン状態であれば）実行
    if "user_id" in session:
        # セッションからuser_idを取得
        user_id = session["user_id"][0]
        # user_idを元にusersテーブルからユーザー名を取得
        get_name = get_list(db_file, "SELECT user_name FROM users WHERE id = ?", (user_id,), False)
        # get_nameがタプル型で取得されるのでユーザー名のみ取り出してuser_nameに代入
        user_name = get_name[0]

        # user_idを元にwordsテーブルからトップいいねの言葉を取得
        get_top = get_list(db_file, "SELECT id, date, word, good FROM words WHERE user_id = ? AND del_flag = 0 ORDER BY good DESC LIMIT 1", (user_id,), False)
        if get_top is None:
            # get_topがNoneの場合（新規ユーザーが最初にログインした状態）top_goodにNoneを格納
            top_good = None
        else:
            # get_topが存在した場合にtop_goodに辞書型で格納
            # 登録日時は秒を省略する
            # SQLiteでは日付がテキスト型で保存されるのでいったんdatetimeクラスに変換してから秒を省略した書式に変更
            top_dt = datetime.datetime.strptime(get_top[1], '%Y年%m月%d日 %H:%M:%S').strftime('%Y年%m月%d日 %H:%M')
            top_good = {"id":get_top[0], "date":top_dt, "word":get_top[2], "good":get_top[3]}

        # 表示順に合わせてwordsテーブルから言葉のリストを取得
        if order == "regist":
            # 登録順の場合
            acquisition = get_list(db_file, "SELECT id, date, word, good FROM words WHERE user_id = ? AND del_flag = 0 ORDER BY date DESC", (user_id,), True)
        elif order == "good":
            # いいね順の場合
            acquisition = get_list(db_file, "SELECT id, date, word, good FROM words WHERE user_id = ? AND del_flag = 0 ORDER BY good DESC", (user_id,), True)
        else:
            return redirect("/")
        
        word_list = []
        for row in acquisition:
            # 取得したレコードを辞書型に変換して、word_listに追加
            # 登録日時は秒を省略する
            # SQLiteでは日付がテキスト型で保存されるのでいったん日付に変換してから秒を省略した書式に変換
            dt = datetime.datetime.strptime(row[1], '%Y年%m月%d日 %H:%M:%S').strftime('%Y年%m月%d日 %H:%M')
            word_list.append({"id":row[0], "date":dt, "word":row[2], "good":row[3]})

        # 表示する順をsessionに記録
        session["page"] = order

        # 表示順に合わせてリストのページを表示
        if order == "regist":
            # 登録順の場合
            return render_template("list_chronological_order.html", top_good = top_good, word_list = word_list, user_name = user_name, user_id = user_id)
        elif order == "good":
            # いいね順の場合
            return render_template("list_good_order.html", word_list = word_list, user_name = user_name, user_id = user_id)
        else:
            return redirect("/")
    else:
        return redirect("/")

# 言葉を登録
# 登録日時は秒単位で記録
@app.route("/add", methods = ["POST"])
def add_post():
    if "user_id" in session:
        # セッション内にuser_idがあれば（ログイン状態であれば）実行
        # dateにボタンを押した時点の時刻を"0000年00月00日 00:00:00"の様式で格納
        date = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        # フォームから登録する言葉を取得
        word = request.form.get("word")
        # セッションからuser_idを取得
        user_id = session["user_id"][0]
        # wordsテーブルに新規の言葉のレコードを追加
        add_record(db_file, "INSERT INTO words VALUES (null, ?, ?, ?, 0, 0)", (date, word, user_id))
        # セッションから現在表示している順序を取得してリダイレクト
        page = session["page"]
        return redirect("/list/" + page)
    else:
        return redirect("/")

# いいねを1増やす
@app.route("/good/<int:id>")
def good(id):
    if "user_id" in session:
        # セッション内にuser_idがあれば（ログイン状態であれば）実行
        user_id = session["user_id"][0]
        # 言葉のidとuser_idを元にwordsテーブルからいいね数を取得
        good = get_list(db_file, "SELECT good FROM words WHERE id = ? AND user_id = ? AND del_flag = 0", (id, user_id), False)
        if good is None:
            # 該当する言葉がなかった場合にセッションから現在表示している順序を取得してリダイレクト > アドレスをベタ打ちでいいね数を増加させるのを回避
            page = session["page"]
            return redirect("/list/" + page)

        # goodがタプル型で取得されるのでいいね数のみ取り出してgood_countに代入し1増加
        good_count = good[0]
        good_count += 1

        # wordsテーブルの該当する言葉のいいね数を更新
        update_record(db_file, "UPDATE words SET good = ? WHERE id = ? AND user_id = ? AND del_flag = 0", (good_count, id, user_id))

        # セッションから現在表示している順序を取得してリダイレクト
        page = session["page"]
        return redirect("/list/" + page)

# 言葉を削除
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" in session:
        # セッション内にuser_idがあれば（ログイン状態であれば）実行
        user_id = session["user_id"][0]
        # 言葉のidとuser_idを元にwordsテーブルの該当する言葉のdef_flagを1に更新 > アドレスをベタ打ちでいいね数を増加させるのを回避
        update_record(db_file, "UPDATE words SET del_flag = 1 WHERE id = ? AND user_id = ? AND del_flag = 0", (id, user_id))

        # セッションから現在表示している順序を取得してリダイレクト
        page = session["page"]
        return redirect("/list/" + page)
    else:
        return redirect("/")

# ログアウト
@app.route("/logout")
def logout():
    # セッションを削除しトップページへリダイレクト
    session.pop("user_id", None)
    return redirect("/")

# 関数

# データベースからリストを取得
# db_file:データベースのファイル名
# query:SQLのクエリ(SELECT)
# terms:クエリ内の?に代入する値
# fetchall:クエリで取得した結果を fetchall()で受け取る場合はTrue fetchone()で受け取る場合はFalse
def get_list(db_file, query, terms, fetchall):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(query, terms)
    if fetchall is True:
        list = c.fetchall()
    elif fetchall is False:
        list = c.fetchone()
    else:
        list = None
    c.close()
    return list

# データベースにレコードを追加
# db_file:データベースのファイル名
# query:SQLのクエリ(INSERT)
# terms:クエリ内の?に代入する値
def add_record(db_file, query, terms):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(query, terms)
    conn.commit()
    c.close()

# データベースのレコードを更新
# db_file:データベースのファイル名
# query:SQLのクエリ(UPDATE)
# terms:クエリ内の?に代入する値
def update_record(db_file, query, terms):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(query, terms)
    conn.commit()
    c.close()

# スクリプトとして直接実行した場合
if __name__ == "__main__":
    # FlaskのWEBアプリケーションを起動
    app.run(debug=True)