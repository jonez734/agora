<?php
/**
 * class to handle amazon items.
 *
 * @since 20190901
 * @author Zoid Technologies
 * @copyright Copyright (c) 2002-2019 Zoid Technologies. All Rights Reserved.
 * @package agora
 */

require_once("config.php");
require_once("libagora.php");
require_once("zoidweb4.php");
require_once("bbsengine4.php");

// require_once("Pager/Pager.php");

class amznitem
{
    var $dbh = false;

    function comment()
    {
      if (flag("AUTHENTICATED") === false)
      {
        displaypermissiondenied();
        return;
      }
    }

    function insert($values)
    {
//      $this->dbh->beginTransaction();

      $node = [];
      $node["datecreated"] = "now()";
      $node["createdbyid"] = getcurrentmemberid();
      $node["sigs"] = buildsiglist($values["sigs"]);

      $amznitem = buildamznitemrecord($values);
      logentry("agora.amznitem.insert.25: amznitem=".var_export($amznitem, true));

      $node["attributes"] = $amznitem;
      $nodeid = insertnode($node);
      // $res = $this->dbh->autoExecute("engine.__node", $amznitem, MDB2_AUTOQUERY_INSERT);
      if (PEAR::isError($nodeid))
      {
        logentry("agora.amznitem.14: " . $nodeid->toString());
        return PEAR::raiseError("database error (code: agora.amznitem.14)");
      }
      displayredirectpage("OK -- amazon item inserted");
      return true;

    }

    function add()
    {
      if (flag("ADMIN") === false)
      {
        displaypermissiondenied();
        return;
      }

      setcurrentaction("add");
      setcurrentpage("amznitem-add");

      $form = getquickform("amznitem-add", "post", ["action" => "/amznitem-add"]);

      $const = [];
      $const["mode"] = "add";
      $const["memberid"] = getcurrentmemberid();

      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

      buildamznitemfieldset($form);

      $form->addElement("submit", "addamznitem", ["value" => "add amznitem"]);

      $res = handleform($form, [$this, "insert"], "add amznitem");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitem.400: " . $res->toString());
        return PEAR::raiseError("error handling form (code: agora.amznitem.400)");
      }
      if ($res === true)
      {
        logentry("agora.amznitem.402: handleform(...) returned true");
        return true;
      }
      $renderer = getquickformrenderer();
      $form->render($renderer);
      $res = displayform($renderer, "add amznitem");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitem.404: " . $res->toString());
        return PEAR::raiseError("error displaying form (code: agora.amznitem.404)");
      }
      return $res;
    }

    function update($values)
    {
//      var_export($values);
//      $sigs = explodesiglabelpaths($values["sigs"]); // trimed and filtered array of sigpaths
      $amznitem = buildamznitemrecord($values);
      if (PEAR::isError($amznitem))
      {
        logentry("amznitem.200: " . $amznitem->toString());
        displayerrorpage("unable to build amznitem record (code: amznitem.200)");
        return false;
      }

      $nodeid = $values["id"];
      logentry("amznitem.update.220: nodeid=".var_export($nodeid, true));

      // validatesigs() expects a string of sigs separated by commas
      $sigs = $values["sigs"];
      logentry("amznitem.update.240: sigs=".var_export($sigs, true));
      $sigslist = buildsiglist($sigs);
      if (validatesigs($sigslist) === false)
      {
        logentry("amznitem.280: sigslist=".var_export($sigslist, true)." does not validate");
        return false;
      }

      $this->dbh->beginTransaction();

      // $amznitem["attributes"];

      $node = [];
      $node["dateupdated"] = "now()";
      $node["updatedbyid"] = getcurrentmemberid();
      $node["attributes"] = $amznitem; // updatenode() encodes attributes to json
      $node["sigs"] = $sigslist;

      $res = updatenode($nodeid, $node);
      if (PEAR::isError($res))
      {
        logentry("amznitem.update.120: " . $res->toString());
        $this->dbh->rollback();
        return $res;
      }
      $this->dbh->commit();
      displayredirectpage("OK -- amazon item updated");
      return true;
    }

    function edit()
    {
      if (flag("ADMIN") ===  false)
      {
        displaypermissiondenied();
        return;
      }

      $asin = isset($_REQUEST["asin"]) ? $_REQUEST["asin"] : null;
      $nodeid = isset($_REQUEST["nodeid"]) ? $_REQUEST["nodeid"] : null;

      $this->dbh = dbconnect(SYSTEMDSN);
      if (PEAR::isError($this->dbh))
      {
        logentry("amznitem.100: " . $this->dbh->toString());
        return PEAR::raiseError("database connect error (code: amznitem.100)");
      }

      $amznitem = getamznitembynodeid($nodeid);
      if (PEAR::isError($amznitem))
      {
        logentry("amznitem.120: " . $amznitem->toString());
        return PEAR::raiseError("could not get amznitem ".var_export($nodeid, true)." from database (code: amznitem.120)");
      }

      if ($amznitem === null)
      {
        logentry("amznitem.140: getamznitembyid(".var_export($nodeid, true).") returned null.");
        return PEAR::raiseError("Input Error (code: amznitem.140)");
      }

      if (accessamznitem("edit", $amznitem) === false)
      {
        displaypermissiondenied();
        return;
      }

//      setreturnto(getreturntourl());
      setcurrentaction("edit");
      setcurrentpage("amznitem-edit");

      $sigslist = $amznitem["sigs"];
      $amznitem["sigs"] = implodesigmap($sigslist);

      $form = getquickform("amznitem-edit", "post", ["action" => "/amznitem-edit-{$nodeid}"]);

/*
      logentry("amznitem.160: amznitem.sigs=".var_export($amznitem["sigs"], true));
      $sigmap = getamznitemsigmap($amznitem["id"]);
      if (PEAR::isError($sigmap))
      {
        logentry("amznitem.102: " . $sigs->toString());
        return $sigmap;
      }
      logentry("amznitem.103: sigmap=".var_export($sigmap, True));

      $amznitem["sigs"] = implodesigmap($sigmap);

      logentry("amznitem.500: agora.amznitem.sigs=".var_export($amznitem["sigs"], True));
*/
      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($amznitem));

      $const = [];
      $const["mode"] = "edit";
      $const["memberid"] = getcurrentmemberid();
      $const["id"] = $amznitem["id"];
      
      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

      buildamznitemfieldset($form); // , ["uniqueurlrule" => false]);

      $form->addElement("submit", "editamznitem", ["value" => "update amznitem"]);
      
      $res = handleform($form, [$this, "update"], "edit amznitem");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitem.800: " . $res->toString());
        return PEAR::raiseError("error handling form (code: agora.amznitem.800)");
      }
      if ($res === true)
      {
        logentry("agora.amznitem.802: handleform(...) returned true");
        return true;
      }
      $renderer = getquickformrenderer();
      $form->render($renderer);
      $res = displayform($renderer, "edit amznitem");
      if (PEAR::isError($res))
      {
        logentry("agora.amznitem.804: " . $res->toString());
        return PEAR::raiseError("error displaying form (code: agora.amznitem.804)");
      }
      return $res;
    }

    function main()
    {
      startsession();

      $mode = isset($_REQUEST["mode"]) ? $_REQUEST["mode"] : null;
      if ($mode === null)
      {
        logentry("agora.amznitem.5: mode is null");
        return PEAR::raiseError("input error (code: agora.amznitem.5)");
      }

      $this->dbh = dbconnect(SYSTEMDSN);
      if (PEAR::isError($this->dbh))
      {
        logentry("agora.amznitem.10: " . $this->dbh->toString());
        return PEAR::raiseError("Database Error (code: agora.amznitem.10)");
      }
        
      switch ($mode)
      {
        case "get":
          $res = $this->get();
          break;
        case "edit":
          $res = $this->edit();
          break;
        case "add":
          $res = $this->add();
          break;
        default:
          logentry("agora.amznitem.20: mode=".var_export($mode, true));
          $res = PEAR::raiseError("Input Error (code: agora.amznitem.20)");
          break;
      }
    
      clearcurrentaction();
      
      endsession();
      
      $this->dbh->disconnect();
      return $res;
    }
};

$a = new amznitem();
$b = $a->main();
if (PEAR::isError($b))
{
  logentry("agora.amznitem.100: " . $b->toString());
  displayerrorpage($b->getMessage());
  exit;
}

?>
