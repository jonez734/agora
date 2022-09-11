<?php

require_once("Services/Amazon.php");
require_once("config.php");
$amazon = new Services_Amazon(AMZNACCESSKEY, AMZNSECRETKEY);

$options = array();

$options['ResponseGroup'] = 'Large';

$result = $amazon->ItemLookup('B009GEF8HG', $options);
print $result;
