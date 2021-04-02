create table "__exchange" (
    "id" serial unique not null primary key,
    "name" text not null,
    "type" text not null,
    "description" text,
    "createdbyid" integer constraint fk_exchange_createbyid references engine.__member(id) on update cascade on delete set null,
    "datecreated" timestamptz,
    "lastmodifiedbyid" integer constraint fk_exchange_lastmodifiedbyid references engine.__member(id) on update cascade on delete set null,
    "datelastmodified" timestamptz,
);

create view "exchange" as 
    select __exchange.*,
     extract(epoch from datelastmodified) as datelastmodifiedepoch
    from __exchange
    left join engine.member createdby on createdby.id = __exchange.createdbyid
    left join engine.member lastmodifiedby on lastmodifiedby.id = __exchange.lastmodifiedbyid
;
