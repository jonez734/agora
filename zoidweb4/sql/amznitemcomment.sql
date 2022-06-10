create or replace view agora.amznitemcomment as
    select
        n.*,
        n.attributes->>'asin' as asin,
        extract(epoch from (n.attributes->>'datewatched')::timestamptz) as datewatchedepoch,
        n.attributes->>'datewatched' as datewatched,
        n.attributes->>'watchmethod' as watchmethod,
        n.attributes->>'comment' as comment
    from engine.node as n
    where attributes ? 'datewatched' and attributes ? 'watchmethod' and attributes ? 'comment'
;

grant select on agora.amznitemcomment to apache;
