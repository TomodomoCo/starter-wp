<?php

namespace Tomodomo\Controllers;

use GuzzleHttp\Psr7\Request;

class IndexController extends BaseController
{
    /**
     * @param Request  $request
     * @param Response $response
     * @param array    $args
     *
     * @return string
     */
    public function get(Request $request, $response, array $args) : string
    {
        return $this->twig->compile('index.twig');
    }
}
