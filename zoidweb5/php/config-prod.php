<?php

define("SITETITLE", "agora");
define("SITEADMINEMAIL", "jam <jam@zoidtechnologies.com>");

/**
 * define the base url for the site. THIS VALUE MUST BE TERMINATED WITH A "/"
 */
define("SITEURL", "http://agora.zoidtechnologies.com/");
define("SKINURL", SITEURL . "skin/");
// define("SYSTEMDSN", "pgsql://apache@localhost/zoidweb2");
define("VHOSTDIR", "/srv/www/vhosts/agora.zoidtechnologies.com/");
define("DOCUMENTROOT", VHOSTDIR . "80/html/");

define("IMAGESURL", "http://static.zoidtechnologies.com/");

define("SMARTYCOMPILEDTEMPLATESDIR", VHOSTDIR . "templates_c"); 
define("SMARTYPLUGINSDIR", VHOSTDIR . "smarty/");
define("SMARTYTEMPLATESDIR", "skin/tmpl/");

define("LOGENTRYPREFIX", "agoraprod");
// define("AMZNBASEURL", "http://webservices.amazon.com/onca/xml"); // "http://www.amazon.com/dp/");
define("AMZNBASEURL", "http://www.amazon.com/dp/");
//define("AMZNACCESSKEY", "AKIAJBYO5RZHHHBJH4AQ");
//define("AMZNSECRETKEY", "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");
define("AMZNACCESSKEY", "AKIAIMZLBJ43DU6VLIVQ");
define("AMZNSECRETKEY", "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");
define("AMZNVERSION", "2013-08-01");
define("AMZNASSOCIATETAG", "zoidagora2022-20"); // zoidtechnolog-20");

/*
 * @since 20190722
 */
$includepath = get_include_path();
$zoidweb4 = str_replace("zoidweb3", "zoidweb4", $includepath);
set_include_path($zoidweb4);

/**
 * @since 20200413
 */
define("TEXTAREAMODE", "tinymce");

/**
 * @since 20200422
 * 6
 */
define("GOOGLEANALYTICSACCOUNT", "UA-23705021-1");

?>
