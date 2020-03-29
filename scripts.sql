drop table if exists `availability`;
drop table if exists stores;

create table stores (
    storeID varchar(255) not null,
    storeName varchar(255),
    addr varchar(255),
    latitude decimal(9,6),
    longitude decimal(9,6),
    occupancy int,
    primary key (storeID)
);

create table `availability` (
    store_id varchar(255) not null,
    item_name varchar(255) not null,
    available boolean,
    constraint SI_pair primary key (store_id, item_name),
    foreign key (store_id) references stores(storeID)
);

insert into stores(storeID, storeName, addr, latitude, longitude, occupancy) values("AAA", "Safeway", "666 Wallaby Way", 1, -1, 0);

insert into availability(store_id, item_name, available) values("AAA", "milk", 1);