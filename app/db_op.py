import os
from sqlite3 import connect, Row
import bcrypt

class Database:
    def __init__(self, db_path=r'C:\Projects\flask_app\app\app.db'):
        if not os.path.exists(db_path):
            print("Database file does not exist.")
            exit()
        self.connection = connect(database=db_path)
        self.connection.row_factory = Row  # Enable access by column name
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def user_add(self, username, password):
        add_user = 'INSERT INTO user(username, password) VALUES(?, ?)'
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
            result = self.cursor.execute(add_user, (username, hashed_password))
            if result:
                self.connection.commit()
                print("User added successfully.")
                user_id = self.cursor.lastrowid
                self.profile_add(user_id)
        except Exception as e:
            print(f"Error adding user: {e}")
            return -1

    def user_edit(self, preUsername, newUsername=None, newPassword=None):
        user_id = self.get_user_id(preUsername)
        if user_id is None:
            print("User doesn't exist")
            return -1
        edit_user = 'UPDATE user SET username=?, password=? WHERE id=?'
        self.cursor.execute(edit_user, (newUsername, newPassword, user_id))
        self.connection.commit()

    def user_verify(self, username, password):
        user_id = self.get_user_id(username)
        if user_id is None:
            return -1
        user_hashpw = self.get_password(user_id)
        return bcrypt.checkpw(password.encode('utf-8'), user_hashpw.encode('utf-8'))

    def get_password(self, user_id):
        password_get = 'SELECT password FROM user WHERE id = ?'
        self.cursor.execute(password_get, (user_id,))
        result = self.cursor.fetchone()
        return result['password'] if result else None

    def profile_add(self, user_id=None, email=None, address=None, contact_number=None):
        add_user_profile = 'INSERT INTO user_profile(user_id, email, address, contact_number) VALUES(?, ?, ?, ?)'
        try:
            result = self.cursor.execute(add_user_profile, (user_id, email, address, contact_number))
            if result:
                self.connection.commit()
                print('Profile added successfully')
                return 1
        except Exception as e:
            print(f"Error adding profile: {e}")
            return -1

    def profile_edit(self, username, email=None, address=None, contact_number=None):
        profile_id = self.get_profile_id(username)
        edit_user_profile = 'UPDATE user_profile SET email=?, address=?, contact_number=? WHERE id=?'
        try:
            result = self.cursor.execute(edit_user_profile, (email, address, contact_number, profile_id))
            if result:
                self.connection.commit()
                print('Profile edited successfully')
                return 1
        except Exception as e:
            print(f"Error editing profile: {e}")
            return -1

    def get_user_id(self, username):
        user_id_query = 'SELECT id FROM user WHERE username = ?'
        self.cursor.execute(user_id_query, (username,))
        result = self.cursor.fetchone()
        return result['id'] if result else None

    def get_profile_id(self, username):
        user_id = self.get_user_id(username)
        profile_id_query = 'SELECT id FROM user_profile WHERE user_id = ?'
        self.cursor.execute(profile_id_query, (user_id,))
        result = self.cursor.fetchone()
        return result['id'] if result else None

    def get_user(self, username):
        if username is None:
            return -1
        user_id = self.get_user_id(username)
        user_get = 'SELECT * FROM user WHERE id = ?'
        self.cursor.execute(user_get, (user_id,))
        result = self.cursor.fetchone()
        return result if result else None

    def get_profile(self, username):
        if username is None:
            return -1
        profile_id = self.get_profile_id(username)
        profile_get = 'SELECT * FROM user_profile WHERE id = ?'
        self.cursor.execute(profile_get, (profile_id,))
        result = self.cursor.fetchone()
        return result if result else None

    def add_post(self, user_id, title, body):
        add_post_query = '''
            INSERT INTO post(user_id, title, body, created_at, updated_at)
            VALUES(?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        '''
        try:
            result = self.cursor.execute(add_post_query, (user_id, title, body))
            if result:
                self.connection.commit()
                print("Post added successfully.")
                return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding post: {e}")
            return -1

    def edit_post(self, post_id, title=None, body=None):
        edit_post_query = '''
            UPDATE post
            SET title = COALESCE(?, title),
                body = COALESCE(?, body),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        try:
            result = self.cursor.execute(edit_post_query, (title, body, post_id))
            if result:
                self.connection.commit()
                print("Post edited successfully.")
                return 1
        except Exception as e:
            print(f"Error editing post: {e}")
            return -1

    def delete_post(self, post_id):
        delete_post_query = 'DELETE FROM post WHERE id=?'
        try:
            result = self.cursor.execute(delete_post_query, (post_id,))
            if result:
                self.connection.commit()
                print("Post deleted successfully.")
                return 1
        except Exception as e:
            print(f"Error deleting post: {e}")
            return -1

    def get_post(self, post_id):
        get_post_query = 'SELECT * FROM post WHERE id=?'
        self.cursor.execute(get_post_query, (post_id,))
        result = self.cursor.fetchone()
        return result if result else None

    def get_posts_by_user(self, user_id):
        get_posts_query = 'SELECT * FROM post WHERE user_id=? ORDER BY created_at DESC'
        self.cursor.execute(get_posts_query, (user_id,))
        results = self.cursor.fetchall()
        return results if results else []

    def update_post(self, post_id, title, body):
        post_update = '''update post set title = ? body = ? where post_id=?'''
        
        try:
            self.cursor.execute(post_update, (title, body, post_id))
        except Exception as e:
            print("Database error:", e)
            return -1

    def like_post(self, user_id, post_id):
        try:
            # First check the current reaction state
            self.cursor.execute('''
                SELECT reaction_type FROM post_reactions 
                WHERE user_id = ? AND post_id = ?
            ''', (user_id, post_id))
            current_reaction = self.cursor.fetchone()

            # Update post_reactions table
            if current_reaction:
                # User already reacted - check if it's a dislike that needs to be switched
                if current_reaction[0] == 'dislike':
                    # Switching from dislike to like
                    self.cursor.execute('''
                        UPDATE post_reactions 
                        SET reaction_type = 'like', timestamp = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND post_id = ?
                    ''', (user_id, post_id))
                    # Decrease dislikes and increase likes
                    self.cursor.execute('''
                        UPDATE post 
                        SET dislikes = dislikes - 1, likes = likes + 1 
                        WHERE id = ?
                    ''', (post_id,))
                elif current_reaction[0] == 'like':
                    # User is unliking (remove the like)
                    self.cursor.execute('''
                        DELETE FROM post_reactions 
                        WHERE user_id = ? AND post_id = ?
                    ''', (user_id, post_id))
                    self.cursor.execute('''
                        UPDATE post SET likes = likes - 1 WHERE id = ?
                    ''', (post_id,))
            else:
                # New like
                self.cursor.execute('''
                    INSERT INTO post_reactions (user_id, post_id, reaction_type)
                    VALUES (?, ?, 'like')
                ''', (user_id, post_id))
                self.cursor.execute('''
                    UPDATE post SET likes = likes + 1 WHERE id = ?
                ''', (post_id,))

            self.connection.commit()
            return 1
        except Exception as e:
            print(f"Error in like_post: {e}")
            self.connection.rollback()
            return -1

    def dislike_post(self, user_id, post_id):
        try:
            # First check the current reaction state
            self.cursor.execute('''
                SELECT reaction_type FROM post_reactions 
                WHERE user_id = ? AND post_id = ?
            ''', (user_id, post_id))
            current_reaction = self.cursor.fetchone()

            # Update post_reactions table
            if current_reaction:
                # User already reacted - check if it's a like that needs to be switched
                if current_reaction[0] == 'like':
                    # Switching from like to dislike
                    self.cursor.execute('''
                        UPDATE post_reactions 
                        SET reaction_type = 'dislike', timestamp = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND post_id = ?
                    ''', (user_id, post_id))
                    # Decrease likes and increase dislikes
                    self.cursor.execute('''
                        UPDATE post 
                        SET likes = likes - 1, dislikes = dislikes + 1 
                        WHERE id = ?
                    ''', (post_id,))
                elif current_reaction[0] == 'dislike':
                    # User is undisliking (remove the dislike)
                    self.cursor.execute('''
                        DELETE FROM post_reactions 
                        WHERE user_id = ? AND post_id = ?
                    ''', (user_id, post_id))
                    self.cursor.execute('''
                        UPDATE post SET dislikes = dislikes - 1 WHERE id = ?
                    ''', (post_id,))
            else:
                # New dislike
                self.cursor.execute('''
                    INSERT INTO post_reactions (user_id, post_id, reaction_type)
                    VALUES (?, ?, 'dislike')
                ''', (user_id, post_id))
                self.cursor.execute('''
                    UPDATE post SET dislikes = dislikes + 1 WHERE id = ?
                ''', (post_id,))

            self.connection.commit()
            return 1
        except Exception as e:
            print(f"Error in dislike_post: {e}")
            self.connection.rollback()
            return -1

    # get user with similar liking
    def get_similar_users(self, user_id, limit=3):
        """Find users who liked similar posts"""
        self.cursor.execute('''
            SELECT pr2.user_id, COUNT(*) as common_likes
            FROM post_reactions pr1
            JOIN post_reactions pr2 ON pr1.post_id = pr2.post_id
            WHERE pr1.user_id = ? 
            AND pr2.user_id != ?
            AND pr1.reaction_type = 'like'
            AND pr2.reaction_type = 'like'
            GROUP BY pr2.user_id
            ORDER BY common_likes DESC
            LIMIT ?
        ''', (user_id, user_id, limit))
        return self.cursor.fetchall()

    #now get the post from similar user
    def get_recommendations_from_similar_users(self, user_id, limit=5):
        """Get posts liked by similar users"""
        similar_users = self.get_similar_users(user_id)
        if not similar_users:
            return self.get_popular_posts(limit)
        
        similar_user_ids = [str(user[0]) for user in similar_users]
        
        self.cursor.execute('''
            SELECT p.*, COUNT(*) as recommendation_score
            FROM post p
            JOIN post_reactions pr ON p.id = pr.post_id
            WHERE pr.user_id IN ({})
            AND p.id NOT IN (
                SELECT post_id FROM post_reactions 
                WHERE user_id = ? AND reaction_type = 'dislike'
            )
            AND p.id NOT IN (
                SELECT post_id FROM post_reactions 
                WHERE user_id = ? AND reaction_type = 'like'
            )
            GROUP BY p.id
            ORDER BY recommendation_score DESC, p.likes DESC
            LIMIT ?
        '''.format(','.join(['?']*len(similar_user_ids))), 
        similar_user_ids + [user_id, user_id, limit])
        
        return self.cursor.fetchall()

    