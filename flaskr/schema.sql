DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS entries;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT,
  first_name TEXT,
  last_name TEXT,
  course TEXT,
  type TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

INSERT INTO users('username', 'password','first_name', 'last_name', 'type') 
VALUES ('admin', 'pbkdf2:sha256:600000$YZDx6yNdjZWkV9oq$b688db58b78f9269ce397a5a92cec765c294e35517eb77f379dfffd7977a6ca1', 'Super', 'Admin', 'admin')
