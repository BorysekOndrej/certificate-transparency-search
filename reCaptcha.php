<?php

function reCaptchaPrint()
{
    echo '<div class="g-recaptcha" data-sitekey="' . recaptchaSiteKey() . '"></div>';
}

function reCaptchaValidate()
{
    if (!isset($_POST["g-recaptcha-response"])) {
        return false;
    }
    $url = 'https://www.google.com/recaptcha/api/siteverify';
    $data = array(
        'secret' => recaptchaSecret(),
        'response' => $_POST["g-recaptcha-response"],
    );
    $options = array(
        'http' => array(
            'header' => "Content-Type: application/x-www-form-urlencoded\r\n",
            'method' => 'POST',
            'content' => http_build_query($data),
        ),
    );
    $context = stream_context_create($options);
    $verify = file_get_contents($url, false, $context);
    $captcha_success = json_decode($verify);
    if ($captcha_success->success == true) {
        return true;
    }
    return false;
}

function reCaptchaValidateNice()
{
    if (reCaptchaValidate() != true) {
        echo "There is a problem with reCAPTCHA";
        return false;
    }
    return true;
}
