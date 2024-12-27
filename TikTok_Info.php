<?php
header('Content-Type: application/json');
$username = $_GET['username'];
$ch = curl_init();

$url = 'https://www.highsocial.com/wp-admin/admin-ajax.php';

$headers = [
    'accept: */*',
    'accept-language: en-US,en;q=0.9',
    'cache-control: no-cache',
    'content-type: application/x-www-form-urlencoded; charset=UTF-8',
    'origin: https://www.highsocial.com',
    'pragma: no-cache',
    'priority: u=1, i',
    'referer: https://www.highsocial.com/find-tiktok-user-id/',
    'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile: ?0',
    'sec-ch-ua-platform: "Windows"',
    'sec-fetch-dest: empty',
    'sec-fetch-mode: cors',
    'sec-fetch-site: same-origin',
    'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-requested-with: XMLHttpRequest'
];

$postData = "action=get_user_account_id&username=$username";

curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

$response = curl_exec($ch);
echo $response;
curl_close($ch);
?>

