<?php

/**
 * class to handle amazon items.
 *
 * @since 20190930
 * @author Zoid Technologies
 * @copyright Copyright (c) 2002-2019 Zoid Technologies. All Rights Reserved.
 * @package agora
 */

require_once("config.php");
require_once("libagora.php");
require_once("zoidweb4.php");
require_once("bbsengine4.php");

// require_once("Pager/Pager.php");

class amznitemcomment
{
    var $dbh = False;

    function update($values)
    {
      $amznitemcomment = buildamznitemcommentrecord($values);
      $nodeid = $values["id"];
      $parentid = $values["parentid"];

      $this->dbh->beginTransaction();

      logentry("amznitemcomment.update.120: amznitemcomment=" . var_export($amznitemcomment, true));

      $currentmemberid = getcurrentmemberid();

      $node = [];
      $node["parentid"] = $parentid;
      $node["attributes"] = $amznitemcomment;
      $node["dateupdated"] = "now()";
      $node["updatedbyid"] = $currentmemberid;
      $res = updatenode($nodeid, $node);
      if (PEAR::isError($res))
      {
        logentry("amznitemcomment.update.140: ".var_export($res, true));
        return $res;
      }
      
      $this->dbh->commit();

      displayredirectpage("OK -- amazon item comment updated");

      return true;
    }

    function edit()
    {
      if (flag("AUTHENTICATED") === false)
      {
        displaypermissiondenied();
        return;
      }

      $nodeid = isset($_REQUEST["nodeid"]) ? $_REQUEST["nodeid"] : null;
      $node = getnode($this->dbh, $nodeid);
      if (PEAR::isError($node))
      {
        logentry("amznitemcomment.edit.100: " . var_export($node, true));
        return $node;
      }
      if ($node === null)
      {
        logentry("amznitemcomment.edit.120: nodeid=".var_export($nodeid, true)." returned null");
        return false;
      }

      setcurrentaction("edit");
      setcurrentpage("amznitemcomment");
      
      $form = getquickform("amznitemcomment-edit", "post", ["action" => "/amznitemcomment-edit-{$nodeid}"]);

      $attributes = $node["attributes"];
      $data = ["comment" => $attributes["comment"], "id" => $nodeid, "asin" => $attributes["asin"], "watchmethod" => $attributes["watchmethod"], "datewatched" => $attributes["datewatched"]];
      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($data));

      $const = [];
      $const["mode"] = "edit";
      $const["memberid"] = getcurrentmemberid();
      $const["nodeid"] = $nodeid;
      $const["parentid"] = $node["parentid"];
      
      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

      buildamznitemcommentfieldset($form);

      $form->addElement("submit", "editamznitemcomment", ["value" => "edit amznitem comment"]);
      
      $res = handleform($form, [$this, "update"], "edit amznitem comment");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitemcomment.300: " . $res->toString());
        return PEAR::raiseError("error handling form (code: agora.amznitemcomment.300)");
      }
      if ($res === true)
      {
        logentry("agora.amznitemcomment.302: handleform(...) returned True");
        return True;
      }
      $renderer = getquickformrenderer();
      $form->render($renderer);
      $res = displayform($renderer, "edit amznitem comment");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitemcomment.304: " . $res->toString());
        return PEAR::raiseError("error displaying form (code: agora.amznitemcomment.304)");
      }
      return $res;
    }

    function insert($values)
    {
      $this->dbh->beginTransaction();

      $amznitemcomment = buildamznitemcommentrecord($values);

      $node = [];
      $node["parentid"] = $values["parentid"];
      $node["attributes"] = $amznitemcomment;

//      var_export($node);
//      return false;
      $nodeid = insertnode($node);
      if (PEAR::isError($nodeid))
      {
        logentry("amznitemcomment.insert.120: " . $nodeid->toString());
        return $res;
      }

      $this->dbh->commit();

      displayredirectpage("OK -- amazon item comment inserted");

      return true;
    }

    function add()
    {
      if (flag("AUTHENTICATED") === false)
      {
        displaypermissiondenied();
        return;
      }

      $id = isset($_REQUEST["id"]) ? $_REQUEST["id"] : null;
      $parentid = isset($_REQUEST["parentid"]) ? $_REQUEST["parentid"] : null;
//      $asin = isset($_REQUEST["asin"]) ? $_REQUEST["asin"] : null;

      setcurrentaction("add");
      setcurrentpage("amznitemcomment");
      
      $form = getquickform("amznitemcomment-add", "post", ["action" => "/amznitemcomment-add-{$parentid}"]);

      $const = [];
      $const["mode"] = "add";
      $const["memberid"] = getcurrentmemberid();
//      $const["asin"] = $asin;
      $const["parentid"] = $parentid;
      
      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

      buildamznitemcommentfieldset($form);

      $form->addElement("submit", "addamznitemcomment", ["value" => "add amznitem comment"]);
      
      $res = handleform($form, [$this, "insert"], "add amznitem comment");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitemcomment.400: " . $res->toString());
        return PEAR::raiseError("error handling form (code: agora.amznitemcomment.400)");
      }
      if ($res === True)
      {
        logentry("agora.amznitemcomment.402: handleform(...) returned True");
        return True;
      }
      $renderer = getquickformrenderer();
      $form->render($renderer);
      $res = displayform($renderer, "add amznitem comment");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitemcomment.404: " . $res->toString());
        return PEAR::raiseError("error displaying form (code: agora.amznitemcomment.404)");
      }
      return $res;
    }

    function main()
    {
      startsession();

      $mode = isset($_REQUEST["mode"]) ? $_REQUEST["mode"] : null;
      if ($mode === null)
      {
        logentry("agora.amznitemcomment.5: mode is null");
        return PEAR::raiseError("input error (code: agora.amznitemcomment.5)");
      }

      $this->dbh = dbconnect(SYSTEMDSN);
      if (PEAR::isError($this->dbh))
      {
        logentry("agora.amznitemcomment.10: " . $this->dbh->toString());
        return PEAR::raiseError("Database Error (code: agora.amznitemcomment.10)");
      }
        
      switch ($mode)
      {
        case "add":
        {
          $res = $this->add();
          break;
        }
        case "edit":
        {
          $res = $this->edit();
          break;
        }
        default:
          logentry("agora.amznitemcomment.20: mode=".var_export($mode, True));
          $res = PEAR::raiseError("Input Error (code: agora.amznitemcomment.20)");
          break;
      }
    
      clearcurrentaction();
      
      endsession();
      
      $this->dbh->disconnect();
      return $res;
    }

};

$a = new amznitemcomment();
$b = $a->main();
if (PEAR::isError($b))
{
  logentry("agora.amznitemcomment.100: " . $b->toString());
  displayerrorpage($b->getMessage());
  exit;
}
?>
