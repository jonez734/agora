create or replace view agora.item as
    select
        n.*,
        attributes->>'asin' as asin,
        attributes->>'imdbid' as imdbid,
        attributes->>'checks' as checks,
        attributes->>'affiliatelink' as affiliatelink,
        attributes->>'title' as title,
        attributes->>'storeid' as storeid,
        attributes->>'type' as type,
        attributes->>'omdb' as omdb
    from engine.node as n
    where (n.prg = 'agora.item')
    --n.attributes ? 'asin' or n.attributes ? 'imdbid') and n.attributes ? 'checks' and n.attributes ? 'affiliatelink' and n.attributes ? 'title'
;

grant select on agora.item to apache;

-- select COALESCE(NULLIF(attributes->>'asin',''),NULLIF(attributes->>'imdbid','')) as blah from agora.amznitem;
