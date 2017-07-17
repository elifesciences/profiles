<?php
use Symfony\Component\HttpFoundation\Request;
require_once __DIR__.'/../vendor/autoload.php';

$config = include __DIR__.'/../config.php';

$app = new Silex\Application();

$app->get('/', function() use($app, $config) {
    $links = [];
    
    $links["Login with ORCID"] = "https://orcid.org/oauth/authorize?client_id={$config['orcid']['client_id']}&response_type=code&scope=/authenticate&redirect_uri={$config['base_url']}/oauth-url-back";
    
    $output = "<h1>Profiles demo</h1>\n";
    foreach ($links as $label => $href) {
        $output .= "<a href=\"$href\">$label</a>\n";
    }

    return $output;
});

$app->get('/oauth-url-back', function(Request $request) use ($app, $config) {
    $code = $request->query->get('code');
    $client = new GuzzleHttp\Client();
    $response = $client->request('POST', 'https://orcid.org/oauth/token', [
        'form_params' => [
            'client_id' => $config['orcid']['client_id'],
            'client_secret' => $config['orcid']['client_secret'],
            'grant_type' => 'authorization_code',
            'code' => $code,
            'redirect_uri' => $config['base_url'].'/oauth-url-back',
        ],
        'headers' => [
            'Accept' => 'application/json',
        ],
    ]);
    $body = json_decode($response->getBody(), true);
    $token = $body['access_token'];
    $orcid = $body['orcid'];
    $personResponse = $client->request('GET', "https://pub.orcid.org/v2.0/$orcid/person", [
        'headers' => [
            'Accept' => 'application/json',
            'Authorization' => "Bearer $token",
        ],
    ]);
    $person = json_decode($personResponse->getBody(), true);
    $emailResponse = $client->request('GET', "https://pub.orcid.org/v2.0/$orcid/email", [
        'headers' => [
            'Accept' => 'application/json',
            'Authorization' => "Bearer $token",
        ],
    ]);
    $email = json_decode($emailResponse->getBody(), true);
    $employmentsResponse = $client->request('GET', "https://pub.orcid.org/v2.0/$orcid/employments", [
        'headers' => [
            'Accept' => 'application/json',
            'Authorization' => "Bearer $token",
        ],
    ]);
    $employments = json_decode($employmentsResponse->getBody(), true);
    return "<h2>Token response</h2>\n"
        .'<pre>'.var_export($body, true)."</pre>\n"
        ."<h2>/person API</h2>\n"
        .'<pre>'.var_export($person, true).'</pre>'
        ."<h2>/email API</h2>\n"
        .'<pre>'.var_export($email, true).'</pre>'
        ."<h2>/employments API</h2>\n"
        .'<pre>'.var_export($employments, true).'</pre>';
});

$app->get('/ping', function() use($app) {
    return 'pong';
});

$app->error(function($exception) {
    error_log($exception->getMessage()."\n".$exception->getFile().":".$exception->getLine());
});

$app->run();
