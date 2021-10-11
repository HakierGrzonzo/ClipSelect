Create database clip;
Use clip;

CREATE TABLE subs(
    id int PRIMARY KEY AUTO_INCREMENT,
    n int,
    content TEXT,
    series text,
    episode text,
    begin_frame int,
    end_frame int,
    raw_content text
);

CREATE TABLE jobs(
    job_id int primary key AUTO_INCREMENT,
    gif_id int,
    result_filepath int,
    hits int,
    status int
);

CREATE USER 'admin'@'localhost' IDENTIFIED by 'proszeniehackowac';
Grant all privileges on clip.* to 'admin'@'localhost';
CREATE USER 'admin'@'%' IDENTIFIED by 'proszeniehackowac';
Grant all privileges on clip.* to 'admin'@'%';

flush privileges;
