<?php

namespace Tomodomo\Controllers;

class IndexController extends BaseController
{
    /**
     * Handle GET requests to this route
     *
     * @path /
     *
     * @param \GuzzleHttp\Psr7\Request $request
     * @param null $response
     * @param array $args
     * @return string
     */
    public function get($request, $response, $args)
    {
        return $this->twig->compile('index.twig');
    }
}
