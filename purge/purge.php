<?php

require "../vendor/autoload.php";
use GuzzleHttp\Client;

$STRIKETRACKER_URL = getenv('STRIKETRACKER_URL') ? getenv('STRIKETRACKER_URL') : 'https://striketracker.highwinds.com';
if (count($argv) != 2) {
    echo "Usage: php purge.php [account_hash] < urls\n";
    exit(1);
}
$ACCOUNT_HASH = $argv[1];
$client = new Client();

# Grab the Oauth token
if (! getenv('STRIKETRACKER_TOKEN')) {
    echo "Please set the STRIKETRACKER_TOKEN environment variable to your token\n";
    exit(1);
}
$OAUTH_TOKEN = getenv('STRIKETRACKER_TOKEN');

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

# Purge urls
$purge_response = $client->post(
    $STRIKETRACKER_URL . "/api/accounts/$ACCOUNT_HASH/purge",
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
        $STRIKETRACKER_URL . "/api/accounts/$ACCOUNT_HASH/purge/$jobId", [
            'headers' => ["Authorization" => "Bearer $OAUTH_TOKEN"]
        ]);
    $progress = $status_response->json()['progress'];
    $percent = intval($progress * 100.0 / 2);
    printf("\r[%1\$s%2\$s] %3\$s%%", str_repeat('#', $percent), str_repeat(' ', 50 - $percent), intval($progress * 100));
}
echo "\nContent has been purged\n";