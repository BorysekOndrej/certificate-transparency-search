<?php
require_once "config.php";
require_once "CTDomainSearch.php";

if ($recaptchaEnabled) {
    include_once "reCaptcha.php";
    echo "<script src='https://www.google.com/recaptcha/api.js'></script>";
}

?>

<form action="" method="post" enctype="multipart/form-data">
	<input name="searchPattern" placeholder="Input your domain here"/><br>
    <input type="radio" name="searchMode" value="1" checked> Show second level domain names, that were included in the same cert as the search site.<br>
    <input type="radio" name="searchMode" value="2"> Show all domains and subdomains, that were included in the same cert as the search site.<br>
    <input type="radio" name="searchMode" value="3"> Show only subdomains of the search site.<br>
    <?php
if ($recaptchaEnabled) {
    reCaptchaPrint();
}
?>
	<button type="submit" name="submited">Search!</button>
</form>

<?php
if (isset($_POST["submited"]) && isset($_POST["searchPattern"]) && !empty($_POST["searchPattern"]) && isset($_POST["searchMode"])) {
    if ($recaptchaEnabled && reCaptchaValidateNice() == true) {
        $searchPattern = $_POST["searchPattern"];
        $result = array();
        switch ($_POST["searchMode"]) {
            case 1:
                $result = searchForDomains($searchPattern);
                break;
            case 2:
                $result = searchForSubDomains($searchPattern);
                break;
            case 3:
                $result = subdomainsOfSpecificDomain($searchPattern);
                break;
            default:
                echo "unkown search mode";
                break;
        }
        echo 'The output in JSON<div style="border-style: solid;padding: 10px;">' . outputJSON($result) . "</div><br>";
        echo 'The output as a list<div style="border-style: solid;padding: 10px;">';
        foreach ($result as $key => $value) {
            echo $value . "<br>";
        }
        echo '</div><br>';
    }
}
?>

