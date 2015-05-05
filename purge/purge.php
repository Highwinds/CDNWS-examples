<?php

require "../vendor/autoload.php";
use GuzzleHttp\Client;

$HIGHWINDS_URL = getenv('HIGHWINDS_URL') ? getenv('HIGHWINDS_URL') : 'https://striketracker.highwinds.com';
if (count($argv) != 2) {
    echo "Usage: php provision_host.php [account_hash] < urls\n";
    exit(1);
}
$ACCOUNT_HASH = $argv[1];
$client = new Client();

# Check for user credentials
if (! getenv('STRIKETRACKER_USER') || ! getenv('STRIKETRACKER_PASSWORD')) {
    echo "Please set the STRIKETRACKER_USER and STRIKETRACKER_PASSWORD environment variables to your credentials\n";
    exit(1);
}

# Build up purge batch
$urls = [];
while (($line = fgets(STDIN, 4096)) !== false) {
    array_push($urls, [
        "url" => $line
    ]);
}
if (count($urls) == 0) {
    echo "No urls to purge";
    exit(1);
}

# Log in and grab the Oauth token
$auth = $client->post(
    $HIGHWINDS_URL . "/auth/token",
    [
        'body' => [
            "grant_type" => "password",
            "username" => getenv('STRIKETRACKER_USER'),
            "password" => getenv('STRIKETRACKER_PASSWORD')
        ],
        'headers' => [
            "Accept" => "application/json"
        ]
    ]);
$OAUTH_TOKEN = $auth->json()['access_token'];

# Purge urls
$purge_response = $client->post(
    $HIGHWINDS_URL . "/api/accounts/$ACCOUNT_HASH/purge",
    [
        'headers' => ["Authorization" => "Bearer $OAUTH_TOKEN", "Content-Type" => "application/json"],
        'json' => ["list" => $urls]
    ]);
$jobId = $purge_response->json()['id'];
echo "Purge job $jobId submitted\n";

# Poll for status
$progress = 0.0;
while ($progress < 1) {
    $status_response = $client->get(
        $HIGHWINDS_URL . "/api/accounts/$ACCOUNT_HASH/purge/$jobId", [
            'headers' => ["Authorization" => "Bearer $OAUTH_TOKEN"]
        ]);
    $progress = $status_response->json()['progress'];
    $percent = intval($progress * 100.0 / 2);
    printf("\r[%1\$s%2\$s] %3\$s%%", str_repeat('#', $percent), str_repeat(' ', 50 - $percent), intval($progress * 100));
}
echo "\nContent has been purged\n";