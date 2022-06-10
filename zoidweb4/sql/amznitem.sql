create or replace view agora.amznitem as
    select
        n.*,
        attributes->>'asin' as asin,
        attributes->>'imdbid' as imdbid,
        attributes->>'checks' as checks,
        attributes->>'affiliatelink' as affiliatelink,
        attributes->>'title' as title,
        attributes->>'storeid' as storeid
    from engine.node as n
    where (n.attributes ? 'asin' or n.attributes ? 'imdbid') and n.attributes ? 'checks' and n.attributes ? 'affiliatelink' and n.attributes ? 'title'
;

grant select on agora.amznitem to apache;

-- select COALESCE(NULLIF(attributes->>'asin',''),NULLIF(attributes->>'imdbid','')) as blah from agora.amznitem;
