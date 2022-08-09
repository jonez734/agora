create or replace view agora.comment as
    select
        n.*,
        extract(epoch from (n.attributes->>'datewatched')::timestamptz) as datewatchedepoch,
        n.attributes->>'datewatched' as datewatched,
        n.attributes->>'watchmethod' as watchmethod,
        n.attributes->>'comment' as comment
    from engine.node as n
    where n.prg = 'agora.comment'
    --where attributes ? 'datewatched' and attributes ? 'watchmethod' and attributes ? 'comment'
;

grant select on agora.comment to apache;
