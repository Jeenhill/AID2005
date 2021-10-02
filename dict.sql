
create table users (
u_id integer primary key auto_increment,
u_name varchar(30) not null,
u_pw varchar(30)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

create table dict_logs (
log_id int unsigned primary key auto_increment,
log_user varchar(30) not null,
log_word varchar(30),
log_type varchar(20) not null,
log_date timestamp,
log_desc varchar(300)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 ;