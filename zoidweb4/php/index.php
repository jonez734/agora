<?php

require_once("config.php");
require_once("libagora.php");
require_once("zoidweb4.php");
require_once("bbsengine4.php");

function main()
{
    startsession();

    setcurrentsite("agora");
    setcurrentpage("index");
    setcurrentaction("view");
    setreturnto(getcurrenturi());

    $totalItems = getamznitemcount();
    
    if (flag("AUTHENTICATED") == true)
    {
        $perPage = isset($_REQUEST["perPage"]) ? $_REQUEST["perPage"] : intval(floor($totalItems * 0.20));
    }
      
    $params = [];
    $params["mode"] = "Sliding";
    $params["perPage"] = $perPage;
    $params["delta"] = 3;
    $params["totalItems"] = $totalItems;
    $params["curPageSpanPre"] = "[ ";
    $params["curPageSpanPost"] = " ]";
    $params["fileName"] = "index-%d";
    $params["append"] = false;
    $params["path"] = "/";
  
    $pageinfo = buildpageinfo("select id as nodeid, asin from agora.amznitem where not sigs ~ 'top.eros.*' order by datecreated desc", $params);

    $currentpage = isset($_REQUEST["pageID"]) ? $_REQUEST["pageID"] : 1;
    if ($currentpage > 1 && flag("AUTHENTICATED") == true)
    {
        setcurrentpage("index-{$currentpage}");
    }
    else
    {
        setcurrentpage("index");
    }

    $dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($dbh))
    {
        logentry("agora.amznitem.100: " . $dbh->toString());
        displayerrorpage("database connect error (agora.amznitem.100)");
        return;
    }
    $res = $pageinfo["data"];
    logentry("agora.amznitem.200: count(res)=".var_export(count($res), true));

    $items = [];
    foreach ($res as $rec)
    {
        $id = $rec["nodeid"];
        $asin = $rec["asin"];
        $amznitem = getamznitem($asin);
        if (PEAR::isError($amznitem))
        {
            logentry("agora.amznitem.110: " . $xxx->toString());
            break;
        }
        if ($amznitem === null)
        {
            logentry("agora.amznitem.120: getamznitem(".var_export($asin, true).") returned null");
            continue;
        }
        if (accessamznitem("view", $amznitem) === true)
        {
            $comments = getamznitemcomments($id);
            if (PEAR::isError($comments))
            {
                logentry("agora.amznitem.120: " . $comments->toString());
                $comments = [];
            }
            $amznitem["comments"] = $comments;
            $items[] = $amznitem;
        }
    }
    $pageinfo["data"] = $items;

    $data = [];
    $data["pagetemplate"] = "index.tmpl";
    $data["pageinfo"] = $pageinfo;
  
    // logentry("link.500: data=".var_export($data, true));

    $res = displaypage(null, $data);
    if (PEAR::isError($res))
    {
        logentry("amznitem.index.200: " .$res->toString());
    }
    return $res;

    $dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($dbh))
    {
        logentry("index.30: ".$dbh->toString());
        return $dbh;
    }

//    $sql = "select attributes->>'asin' as asin from agora.amznitem order by upper(attributes->>'title') asc";
    $sql = "select id, asin from agora.amznitem order by datecreated desc";
    $res = $dbh->getAll($sql);
    if (PEAR::isError($res))
    {
        logentry("index.20: ".$res->toString());
        return $res;
    }
    if ($res === null)
    {
        logentry("index.40: no amznitems");
        return null;
    }
    $amznitems = [];
    foreach ($res as $rec)
    {
        $parentid = $rec["id"];
        logentry("agora.index.220: parentid=".var_export($parentid, true));
        $asin = $rec["asin"];
//        logentry("index.120: asin=".var_export($asin, true));
/*
        $rec = getamznitem($asin);
        if (PEAR::isError($rec))
        {
            logentry("index.100: " . $rec->toString());
            break;
        }
*/
        $amznitem = buildamznitem($rec);

        if (accessamznitem("view", $amznitem) === false)
        {
            logentry("agora.index.220: skipping amznitem");
            continue;
        }
        logentry("agora.index.200: loading comments");
        $comments = getamznitemcomments($parentid);
        if (PEAR::isError($comments))
        {
            logentry("agora.index.110: " . var_export($comments, true));
            $comments = null;
        }
        $amznitem["comments"] = $comments;
        $amznitems[] = $amznitem;
    }

//    logentry("index.50: items=".var_export($items, true));

    $data = [];
    $data["pagetemplate"] = "index.tmpl";
    $data["items"] = $amznitems;
//    $data["loaded"] = false;
    $data["pagedata"]["sidebarmenu"] = buildsidebarmenu();

    $res = displaypage(null, $data);
    if (PEAR::isError($res))
    {
        logentry("index.40: ".$res->toString());
    }
    return $res;
}

$a = main();
if (PEAR::isError($a))
{
    displayerrorpage($a->getMessage());
    exit;
}

?>
