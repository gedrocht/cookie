<?php
function fetchUrlWithRetries($url, $maxRetries = 2, $delayInSeconds = 2) {
    $retryCount = 0;

    while ($retryCount < $maxRetries) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        if ($httpCode !== 429) {  // If not a 429 error, break the loop
            return $response;
        }

        $retryCount++;
        sleep($delayInSeconds);  // Wait before retrying
    }

    curl_close($ch);
    return false;  // Return false if unable to fetch the URL
}

if (isset($_GET['username'])) {
    $username = $_GET['username'];
    $URL = "&room=" . $username . "&bgcolor=black";

    $content = fetchUrlWithRetries($URL);

    if ($content !== false) {
        echo $content;
    } else {
        echo "<span style='color:white'>Error: Unable to fetch content after multiple retries.</span>";
    }
}
?>
