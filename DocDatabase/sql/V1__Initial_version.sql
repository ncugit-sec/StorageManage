CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    password VARCHAR(128) NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL
);

CREATE TABLE file_type (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    should_upload BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_node (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT,
    owner_id INT NOT NULL,
    type_id INT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES file_node(id),
    FOREIGN KEY (owner_id) REFERENCES user(id),
    FOREIGN KEY (type_id) REFERENCES file_type(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_version (
    id INT PRIMARY KEY AUTO_INCREMENT,
    node_id INT NOT NULL,
    name VARCHAR(256) NOT NULL,
    author_id INT NOT NULL,
    is_uploaded BOOLEAN DEFAULT FALSE NOT NULL,
    FOREIGN KEY (node_id) REFERENCES file_node(id),
    FOREIGN KEY (author_id) REFERENCES user(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_permission (
    id INT PRIMARY KEY AUTO_INCREMENT,
    node_id INT NOT NULL,
    user_id INT NOT NULL,
    can_write BOOLEAN NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    FOREIGN KEY (node_id) REFERENCES file_node(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO file_type (name, should_upload) VALUES ('project', FALSE);
INSERT INTO file_type (name, should_upload) VALUES ('folder', FALSE);
INSERT INTO file_type (name, should_upload) VALUES ('file', TRUE);
