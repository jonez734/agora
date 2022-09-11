<?php

require_once("InputDate.php");
require_once("InputUrl.php");

/**
 * return the count of items to which the current user has access
 *
 * @since 20200412
 * @return integer
 */
function getitemcount()
{
    $dbh = dbconnect(SYSTEMDSN);
    $sql = "select asin from agora.item";
    $res = $dbh->getAll($sql);
    if (PEAR::isError($res))
    {
        logentry("agora.index.getitemcount.100: " . $res->toString());
        return $res;
    }

    $count = 0;
    foreach ($res as $rec)
    {
        if (accessitem("view", $rec) === true)
        {
            $count++;
        }
    }
    return $count;
}

function builditemrecord($values)
{
    $item = [];
    $item["asin"] = $values["asin"];
    $item["imdbid"] = $values["imdbid"];
    $item["checks"] = $values["checks"];
    $item["affiliatelink"] = $values["affiliatelink"];
    $item["title"] = $values["title"];
    
    logentry("builditemrecord.100: " . var_export($item, true));

    return $item;
}

function builditemfieldset($form)
{
    $fieldset = $form->addFieldset("item")->setLabel("Amazon Item");

    $asin = $fieldset->addText("asin", "size=10")->setLabel("ASIN");
    // $asin->addRule("required", "'ASIN' is a required field");

    $imdbid = $fieldset->addText("imdbid", "size=10")->setLabel("IMDBId");

    $title = $fieldset->addText("title", "size=60")->setLabel("Title");
    $title->addRule("required", "'Title' is a required field");

    $affiliatelink = $fieldset->addElement(new HTML_Quickform2_Element_InputUrl("affiliatelink", "size=60"))->setLabel("affiliate link");
#    $affiliatelink->addRule("required", "'affiliate link' is a required field");

    $checks = $fieldset->addText("checks", "size=60")->setLabel("Checks");
    $checks->addRule("required", "'checks' is a required field");

    $sigs = $fieldset->addText("sigs", "size=60")->setLabel("SIGs");
    $sigs->addRule("required", "'SIGs' is a required field");
    $sigs->addRule("callback", "all SIGs must exist", "validatesigs");

    return $form;
}

function builditemcommentrecord($values)
{
    $itemcomment = [];
    $itemcomment["comment"] = $values["comment"];

    $datewatched = $values["datewatched"];
    logentry("builditemcommentrecord.100: datewatched=".var_export($datewatched, true));
    if (is_array($datewatched) === true)
    {
        $itemcomment["datewatched"] = sprintf("%s-%s-%s", $datewatched["Y"], $datewatched["F"], $datewatched["d"]);
    }
    elseif ($datewatched === "")
    {
        $itemcomment["datewatched"] = null;
    }
    else
    {
        $itemcomment["datewatched"] = $datewatched;
    }
    $itemcomment["watchmethod"] = $values["watchmethod"];
    $itemcomment["asin"] = $values["asin"];
    $itemcomment["imdbid"] = $values["imdbid"];

    return $itemcomment;
}

function builditemcommentfieldset($form)
{
    $fieldset = $form->addFieldset("itemcomment")->setLabel("Amazon Item Comment");
    $fieldset->addHidden("asin");
    $fieldset->addHidden("parentid");
    $watchmethod = $fieldset->addText("watchmethod")->setLabel("Watch Method");
    $datewatched = $fieldset->addElement(new HTML_QuickForm2_Element_InputDate("datewatched"))->setLabel("Date Watched");
    $comment = $fieldset->addTextarea("comment", ["rows" => 10, "cols" => 50, "data-editormode" => "tinymce"])->setLabel("Comment");
    $comment->addRule("required", "'comment' is a required field");
//    $datewatched = $fieldset->addElement("date", "datewatched", null, ["format" => "d-F-Y"])->setLabel("Date Watched");
    return $form;
}

function getitemcomments($parentid)
{
    $dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($dbh))
    {
      logentry("libagora.getitemcomments.100: " . $dbh->toString());
      return $dbh;
    }

    $sql = "select * from agora.itemcomment where parentid=".$dbh->quote($parentid, "integer");

    $comments = [];

    $res = $dbh->getAll($sql);
    if (PEAR::isError($res))
    {
        logentry("agora.index.100: " . var_export($res->toString(), true));
        return $res;
    }
    if (count($res) > 0)
    {
        foreach ($res as $rec)
        {
            $itemcomment = decodejson($rec["attributes"]);
            if (accessitemcomment("view", $itemcomment) === true)
            {
              $id = $rec["id"];
              $actions = builditemcommentactions($id, $itemcomment);
              $rec["actions"] = $actions;
              $comments[] = $rec;
            }
        }
    }
    return $comments;
}

/**
 * given an operation and an item dict, returns a boolean to indicate if the operation is allowed.
 *
 * @param $op string
 * @param $item dictionary
 * @param $memberid integer 
 * @since 20190811
 * @since 20200412 moved to libagora from zoidweb4
 * @return boolean
 */
function accessitem($op, $item, $memberid=null)
{
    if ($memberid === null)
    {
        $memberid = getcurrentmemberid();
    }
    switch ($op)
    {
        case "edit":
        {
          if (flag("ADMIN", $memberid) === true)
          {
            $res = true;
            break;
          }
          $res = false;
          break;
        }

        case "view":
        {
          $res = true;
          break;
        }

        default:
        {
            $res = null;
            break;
        }
    }
    return $res;
}

/**
 * builds an array of dictionaries with available actions
 *
 * @param $item dictionary
 * @param $memberid integer
 * @return array
 * @since 20190811
 * @since 20200412 moved to libagora from zoidweb4
 */
function builditemactions($item, $memberid=null)
{
    $asin = $item["asin"];
    $nodeid = $item["id"];

    $actions = [];
    if (accessitem("edit", $item, $memberid) === true)
    {
      $actions[] = ["href" => AGORAURL . "item-edit-{$nodeid}", "title" => "edit item", "class" => "fa fa-edit fa-fw"];
    }
    if (accessitemcomment("add", $item, $memberid) === true)
    {
      $actions[] = ["href" => AGORAURL . "itemcomment-add-{$nodeid}", "title" => "add comment", "class" => "fa fa-comment fa-fw"];
    }
    return $actions;
}

/**
 * builds an array of dictionaries with available actions for the given itemcomment
 *
 * @param $itemcomment dictionary
 * @param $memberid integer
 * @return array
 * @since 20190811
 * @since 20200412 moved to libagora from zoidweb4
 */
function builditemcommentactions($nodeid, $itemcomment)
{
//  logentry("buildamznitemcommentactions.200: nodeid=".var_export($nodeid, true));
  
  $actions = [];
  if (accessitemcomment("edit", $itemcomment) === true)
  {
    $actions[] = ["href" => AGORAURL."itemcomment-edit-{$nodeid}", "title" => "edit comment", "class" => "fa fa-edit fa-fw"];
  }
  if (accessitemcomment("reply", $itemcomment) === true)
  {
    $actions[] = ["href" => AGORAURL."itemcomment-add-{$nodeid}", "title" => "reply to comment", "class" => "fa fa-reply fa-fw"];
  }
  if (accessitemcomment("upvote", $itemcomment) === true)
  {
    $actions[] = ["href" => AGORAURL."itemcomment-upvote-{$nodeid}", "title" => "upvote comment", "class" => "far fa-thumbs-up"];
  }
/*
  if (accessamznitemcomment("downvote", $amznitemcomment) === true)
  {
    $actions[] = ["href" => AGORAURL."amznitemcomment-downvote-{$nodeid}", "title" => "downvote comment", "class" => "far fa-thumbs-down"];
  }
*/
  return $actions;
}

/**
 * given an operation and an itemcomment dict, returns a boolean to indicate if the operation is allowed.
 *
 * @param $op string
 * @param $itemcomment dictionary
 * @param $memberid integer 
 * @since 20190811
 * @since 20200412 moved to libagora from zoidweb4
 * @return boolean
 */
function accessitemcomment($op, $itemcomment, $memberid=null)
{
    if ($memberid === null)
    {
        $memberid = getcurrentmemberid();
    }
    switch ($op)
    {
        case "edit":
        {
          if (flag("ADMIN", $memberid) === true)
          {
            $res = true;
            break;
          }
          $res = false;
          break;
        }
        case "view":
        {
          $res = true;
          break;
        }
        case "add":
        {
          if (flag("AUTHENTICATED"))
          {
            $res = true;
            break;
          }
          $res = false;
          break;

        }
        case "reply":
        {
          if (flag("AUTHENTICATED"))
          {
            $res = true;
            break;
          }
          $res = false;
          break;
        }
        case "upvote":
        {
          if (flag("AUTHENTICATED"))
          {
            $res = true;
            break;
          }
          $res = false;
          break;
        }
        case "downvote":
        {
          if (flag("AUTHENTICATED"))
          {
            $res = true;
            break;
          }
          $res = false;
          break;
        }
        default:
        {
          $res = false;
          logentry("accessitemcomment.100: unknown op ".var_export($op, true));
          break;
        }
    }
    return $res;
}

/*
function buildamznitem($rec)
{
  $amznitem = $rec;
//  $amznitem["attributes"] = decodejson($amznitem["attributes"]);
//  $amznitem["sigs"] = postgres_to_php_array($amznitem["sigs"]);

  $breadcrumbs = [];

  $amznitem["comments"] = [];

  foreach ($rec["sigs"] as $sig)
  {
    $breadcrumb = buildbreadcrumbs($sig);
    $breadcrumbs[] = $breadcrumb;
  }
  $amznitem["breadcrumbs"] = $breadcrumbs;

  $amznitem["actions"] = buildamznitemactions($amznitem);
//  logentry("buildamznitem.100: attributes=".var_export($amznitem["attributes"], true));
  
  return $amznitem;
}
*/

/**
 * function to get an item based on the node id instead of the asin
 *
 * @since 20200419
 * @param integer $nodeid
 * @return item
 */
function getitembynodeid($nodeid)
{
  $dbh = dbconnect(SYSTEMDSN);
  $sql = "select asin from agora.item where id=?";
  $dat = [$nodeid];
  $asin = $dbh->getOne($sql, ["text"], $dat, ["integer"]);
  if (PEAR::isError($asin))
  {
    logentry("getitembynodeid.100: " . $res->toString());
    return $res;
  }
  return getitem($asin);
}

/**
 * returns a record from agora.item for the given asin. automagically decodes item.attributes, assigns item.sigs to a php array, and build breadcrumbs.
 * 
 * @since 20200419
 * @return dict
 */
function getitem($asin)
{
    $dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($dbh))
    {
        logentry("getitem.100: " . var_export($dbh, true));
        return $dbh;
    }

    $sql = "select * from agora.item where asin=?";
    $dat = [$asin];
    $item = $dbh->getRow($sql, null, $dat, ["text"]);
    if (PEAR::isError($item))
    {
        logentry("getitem.120: " . var_export($item, true));
        return $item;
    }
    if ($item === null)
    {
      logentry("getitem.130: query for asin ".var_export($asin, true)." returned null");
      return $item;
    }

    $item["actions"] = builditemactions($item);
    $item["comments"] = [];

    $sigslist = postgres_to_php_array($item["sigs"]);
//    logentry("getamznitem.140: sigslist=".var_export($sigslist, true));
    $breadcrumbs = [];
    foreach ($sigslist as $sig)
    {
      $breadcrumbs[] = buildbreadcrumbs($sig);
    }
    $item["breadcrumbs"] = $breadcrumbs;
    $item["sigs"] = $sigslist;
    $item["attributes"] = decodejson($item["attributes"]);
    return $item;
}

?>
