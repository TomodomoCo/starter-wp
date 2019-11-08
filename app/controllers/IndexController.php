<?php

namespace Tomodomo\Controllers;

use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;
use Timber\PostQuery as Query;

class IndexController extends BaseController
{
    /**
     * Respond to a GET request on the index.
     *
     * @param RequestInterface  $request
     * @param ResponseInterface $response
     * @param array             $args
     *
     * @return ResponseInterface
     */
    public function get(RequestInterface $request, ResponseInterface $response, array $args) : ResponseInterface
    {
        $context = [
            'posts' => new Query(false, '\Tomodomo\Models\Post'),
        ];

        return $this->twig->render($response, 'index.twig', $context);
    }
}
