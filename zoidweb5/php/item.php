<?php

require_once("config.php");
require_once("agora.php");
require_once("zoidweb4.php");
require_once("bbsengine4.php");

require_once("Services/Amazon.php");

class item 
{
    function lookup()
    {
        // call to amzn api to get product  (xml)
        // feed returned values into item.tmpl
        
        $asin = isset($_REQUEST["asin"]) ? $_REQUEST["asin"] : null;
        if ($asin === null)
        {
            logentry("item.100: asin is null");
            return null;
        }

        $params = [];
        $params["Service"] = "AWSECommerceService";
        $params["ItemId"] = $asin;
        $params["ResponseGroup"] = "Medium";
        $params["AssociateTag"] = AMZNASSOCIATETAG;
        
        $amazon = new Services_Amazon(AMZNACCESSKEY, AMZNSECRETKEY);
        $data = $amazon->ItemLookup($asin, $params);
        if (PEAR::isError($data))
        {
            return $data;
        }

        $tmpl = getsmarty();
//        $tmpl->assign("data", $data);
        
        $page = getpage("agora test product page");
        $options = [];
        $options["pagetemplate"] = "testlookup.tmpl";
        foreach ($data as $k => $v)
        {
            $options[$k] = $v;
        }
//        $options["data"] = $data;
        // $options["content"] = $tmpl->fetch("index-content.tmpl");
        $page = getpage("agora test product page", $options);
        displaypage($page, $options);

//        $buf = $tmpl->fetch("item.tmpl");
//        print encodejson($buf);
        return;
    }
    
    function main()
    {
        startsession();
        $mode = $_REQUEST["mode"];
        switch ($mode)
        {
            case "lookup":
            {
                $res = $this->lookup();
                break;
            }
            default:
            {
                $res = PEAR::raiseError("invalid mode");
                break;
            }
        }
        return $res;
    }
};

$a = new item();
$b = $a->main();
if (PEAR::isError($b))
{
    displayerrorpage($b->getMessage());
    exit;
}
?>
