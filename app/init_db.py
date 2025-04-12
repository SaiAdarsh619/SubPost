from sqlite3 import connect


def createdb():
	user_table = '''CREATE TABLE IF NOT EXISTS user (
		id INTEGER PRIMARY KEY,
		username VARCHAR(30) NOT NULL,
		password BLOB NOT NULL
	)'''

	profile_table = '''CREATE TABLE IF NOT EXISTS user_profile (
		id INTEGER PRIMARY KEY,
		user_id INTEGER REFERENCES user(id) on update cascade on delete cascade,
		email VARCHAR(40) CHECK (instr(email, '@') > 0),
		address VARCHAR(60),
		contact_number BIGINT
	)'''

	post_table = '''CREATE TABLE IF NOT EXISTS post (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title VARCHAR(40),
        body TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user(id) ON UPDATE CASCADE ON DELETE CASCADE,
        likes INTEGER DEFAULT 0,
        dislikes INTEGER DEFAULT 0
    )'''

	postreaction_table = '''CREATE TABLE IF NOT EXISTS post_reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    reaction_type TEXT CHECK (reaction_type IN ('like', 'dislike')) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
)'''

	cur.execute(user_table)
	cur.execute(profile_table)
	cur.execute(post_table)
	cur.execute(postreaction_table)
	connection.commit()

if __name__ == '__main__':
	connection = connect(database=r'C:\Projects\flask_app\app\app.db')
	cur = connection.cursor()
	createdb()